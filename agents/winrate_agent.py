from .base_agent import BaseAgent
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import os

class WinRateAgent(BaseAgent):
    """Agent that predicts win probability using ML model"""
    
    def __init__(self):
        super().__init__("WinRateAgent")
        self.model = None
        self.encoders = {}
        self.feature_cols = []
        self.model_path = Path(__file__).parent.parent / "models" / "winrate_model.pkl"
        self.encoders_path = Path(__file__).parent.parent / "models" / "winrate_encoders.pkl"
        
        # Load or train model
        if self.model_path.exists() and self.encoders_path.exists():
            self._load_model()
        else:
            self._train_model()
    
    def _load_data(self) -> pd.DataFrame:
        """Load and prepare training data"""
        data_dir = Path(__file__).parent.parent / "data" / "sample_csv"
        orders_path = data_dir / "orders.csv"
        customers_path = data_dir / "customers.csv"
        products_path = data_dir / "products.csv"
        cogs_path = data_dir / "cogs.csv"
        
        # Load datasets
        orders = pd.read_csv(orders_path)
        customers = pd.read_csv(customers_path)
        products = pd.read_csv(products_path)
        cogs = pd.read_csv(cogs_path)
        
        # Merge data for features
        df = orders.merge(customers, on='customer_id', how='left')
        df = df.merge(products, on='product_id', how='left')
        df = df.merge(cogs, on='product_id', how='left')
        
        # Create features
        df['margin_pct'] = (df['net_price'] - df['cogs']) / df['cogs']
        df['discount_depth'] = df['discount']
        df['price_vs_competitor'] = df['net_price'] / df['competitor_price']
        df['volume_tier'] = pd.cut(df['quantity'], bins=[0, 5, 15, 30, 100], labels=['Small', 'Medium', 'Large', 'XLarge'])
        df['price_position'] = pd.cut(df['price_vs_competitor'], bins=[0, 0.9, 1.1, 2.0], labels=['Below', 'Match', 'Above'])
        
        return df
    
    def _train_model(self):
        """Train the win rate prediction model"""
        print("Training WinRate model...")
        df = self._load_data()
        
        # Feature engineering
        self.feature_cols = [
            'margin_pct', 'discount_depth', 'price_vs_competitor', 'quantity',
            'segment', 'channel', 'region', 'family', 'volume_tier', 'price_position'
        ]
        
        # Encode categorical features
        categorical_cols = ['segment', 'channel', 'region', 'family', 'volume_tier', 'price_position']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = df[col].astype(str)
                df[col + '_encoded'] = le.fit_transform(df[col])
                self.encoders[col] = le
        
        # Prepare features
        feature_cols_encoded = [col + '_encoded' if col in categorical_cols else col for col in self.feature_cols]
        X = df[feature_cols_encoded].fillna(0)
        y = df['won_flag']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred_proba)
        
        print(f"WinRate Model AUC: {auc:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.encoders, self.encoders_path)
        
        print(f"Model saved to {self.model_path}")
    
    def _load_model(self):
        """Load pre-trained model"""
        self.model = joblib.load(self.model_path)
        self.encoders = joblib.load(self.encoders_path)
        self.feature_cols = [
            'margin_pct', 'discount_depth', 'price_vs_competitor', 'quantity',
            'segment', 'channel', 'region', 'family', 'volume_tier', 'price_position'
        ]
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict win probability for given context"""
        # Extract context
        proposed_price = context.get('proposed_price', context.get('target_price', 100))
        competitor_price = context.get('competitor_price', proposed_price * 1.05)
        cogs = context.get('cogs', 80)
        quantity = context.get('quantity', 10)
        segment = context.get('customer_segment', 'Enterprise')
        channel = context.get('channel', 'Direct')
        region = context.get('region', 'EMEA')
        product_family = context.get('product_family', 'Widgets')
        
        # Calculate features
        margin_pct = (proposed_price - cogs) / cogs if cogs > 0 else 0
        discount_depth = max(0, (context.get('list_price', proposed_price * 1.2) - proposed_price) / context.get('list_price', proposed_price * 1.2))
        price_vs_competitor = proposed_price / competitor_price if competitor_price > 0 else 1.0
        
        # Volume and price tiers
        if quantity <= 5:
            volume_tier = 'Small'
        elif quantity <= 15:
            volume_tier = 'Medium'
        elif quantity <= 30:
            volume_tier = 'Large'
        else:
            volume_tier = 'XLarge'
            
        if price_vs_competitor < 0.9:
            price_position = 'Below'
        elif price_vs_competitor <= 1.1:
            price_position = 'Match'
        else:
            price_position = 'Above'
        
        # Create feature vector
        features = {
            'margin_pct': margin_pct,
            'discount_depth': discount_depth,
            'price_vs_competitor': price_vs_competitor,
            'quantity': quantity,
            'segment': segment,
            'channel': channel,
            'region': region,
            'family': product_family,
            'volume_tier': volume_tier,
            'price_position': price_position
        }
        
        # Encode categorical features
        categorical_cols = ['segment', 'channel', 'region', 'family', 'volume_tier', 'price_position']
        for col in categorical_cols:
            if col in self.encoders:
                try:
                    features[col + '_encoded'] = self.encoders[col].transform([features[col]])[0]
                except ValueError:
                    # Handle unseen categories
                    features[col + '_encoded'] = 0
            else:
                features[col + '_encoded'] = 0
        
        # Prepare model input
        feature_cols_encoded = [col + '_encoded' if col in categorical_cols else col for col in self.feature_cols]
        X = np.array([[features[col] for col in feature_cols_encoded]])
        
        # Predict
        win_probability = self.model.predict_proba(X)[0, 1]
        
        # Get feature importance insights
        feature_importance = dict(zip(feature_cols_encoded, self.model.feature_importances_))
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        result = {
            'win_probability': round(win_probability, 3),
            'confidence': 'High' if max(self.model.predict_proba(X)[0]) > 0.7 else 'Medium',
            'key_factors': [f"{feat.replace('_encoded', '')}: {imp:.3f}" for feat, imp in top_features],
            'model_features': features,
            'reasons': [
                f"ML model prediction: {win_probability:.1%}",
                f"Key factor: {top_features[0][0].replace('_encoded', '')}",
                f"Price vs competitor: {price_vs_competitor:.2f}"
            ]
        }
        
        self.log_execution(context, result)
        return result
    
    def get_win_curve(self, context: Dict[str, Any], price_range: List[float]) -> List[Dict[str, float]]:
        """Generate win probability curve for price range"""
        curve_points = []
        
        for price in price_range:
            price_context = context.copy()
            price_context['proposed_price'] = price
            result = self.execute(price_context)
            curve_points.append({
                'price': round(price, 2),
                'p_win': result['win_probability']
            })
        
        return curve_points
