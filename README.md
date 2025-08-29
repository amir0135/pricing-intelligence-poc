# Pricing Intelligence POC

This project demonstrates a **multi-model agent architecture** for pricing intelligence, featuring:
- Backend API with FastAPI and trained ML models
- Power BI PBIP project for analytics and simulation  
- Copilot for Microsoft 365 plugin with OpenAPI actions

## 🎯 Multi-Model Agent Architecture

Unlike single-model solutions, this POC showcases how **multiple specialized agents** work together:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Rules Agent   │    │  WinRate Agent   │    │ Elasticity Agent│
│                 │    │                  │    │                 │
│ • Policy bounds │    │ • ML prediction  │    │ • Price elasticity│
│ • Approval bands│    │ • Feature importance│  │ • Demand curves │
│ • Compliance    │    │ • Confidence scores│  │ • Revenue impact│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Agent Orchestrator │
                    │                     │
                    │ • Coordinates agents│
                    │ • Optimizes expected│
                    │   margin           │
                    │ • Merges insights  │
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │  Explainer Agent    │
                    │                     │
                    │ • Natural language  │
                    │ • Reasoning chains  │
                    │ • Seller talking pts│
                    └─────────────────────┘
```

## Features
- **Rules Agent**: Business policy enforcement (floor/ceiling, approval bands)
- **WinRate Agent**: ML-powered win probability prediction (RandomForest)  
- **Elasticity Agent**: Economic price sensitivity modeling
- **Explainer Agent**: Natural language explanations for transparency
- **Orchestrator**: Coordinates all agents for optimal recommendations

## How to Run Locally
1. Install Python 3.11
2. `pip install -r requirements.txt`
3. `make demo`  # Trains model and starts API
4. Call endpoints:
   - `POST http://localhost:8080/api/recommend`
   - `GET  http://localhost:8080/api/curve?sku=SKU-001&customer_id=C-100&quantity=10&country=DE&channel=Direct`

## Train the ML Model
- Open `notebooks/02_win_model.ipynb` in Jupyter
- Run all cells to train RandomForest on sample data
- Model saves to `models/` folder automatically
- AUC typically ~0.85+ on test data

## Power BI Project
- Open `powerbi/pricing-report` in Power BI Desktop (PBIP format)
- Dataflows load CSVs from `data/sample_csv`
- **Quote Simulator** page shows win curves and recommendations
- Later: integrate live API calls via Power Query/Power Automate

## OAuth Registration
- Register the API in Entra ID (Azure AD)
- Set redirect URIs and expose scope: `api://pricing-poc/user_impersonation`

## Copilot Studio Plugin
- Create a plugin in Copilot Studio
- Choose OpenAPI, upload `copilot-plugin/api-reference.yaml`
- Set OAuth to the same app registration
- Test actions: GetPriceRecommendation, GetWinCurve

## Why Multi-Model Agents Matter for Pricing

**Traditional approach**: One ML model predicts price → limited transparency, brittle

**Multi-agent approach**: 
- **Transparency**: "Target comes from ML model, within policy bounds, elasticity shows 5% demand drop"
- **Flexibility**: Swap models without breaking API
- **Business control**: Policy agent ensures AI never breaks rules
- **Copilot integration**: Natural language queries route to right models

Example Copilot conversation:
> **User**: "Why is the target price lower in France this month?"  
> **Agent**: Routes to elasticity model → finds high price sensitivity  
> **Explainer**: "French market shows -1.8 elasticity vs -1.2 in Germany, so 10% price increase causes 18% demand drop. Target optimizes for volume."

---

**Next Steps**: Deploy to Azure Container Apps, connect to real CRM data, add competitor price feeds.
