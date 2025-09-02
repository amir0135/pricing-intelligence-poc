# Pricing Intelligence Showcase UI

An interactive web interface showcasing the enterprise pricing intelligence system with multi-agent AI recommendations.

## Features

🎯 **Interactive Demonstrations**
- Single product pricing with AI agent insights
- Bulk processing simulation (up to 1000 products)
- Market analysis and trends
- Microsoft 365 Copilot integration demo

🏢 **Enterprise Capabilities**
- Real-time pricing calculations
- Multi-agent system coordination
- Advanced analytics and reporting
- ERP system integration ready

🎨 **Modern Interface**
- Responsive design for all devices
- Real-time animations and feedback
- Professional enterprise styling
- Intuitive user experience

## Quick Start

1. **Install Dependencies**
   ```bash
   cd web-ui
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python app.py
   ```

3. **Access the Interface**
   Open your browser to: http://localhost:5000

## Architecture

- **Frontend**: Modern HTML5/CSS3/JavaScript with responsive design
- **Backend**: Flask server with CORS support
- **Integration**: REST API endpoints for pricing calculations
- **Styling**: CSS Grid, Flexbox, and smooth animations

## API Endpoints

- `GET /` - Main showcase interface
- `GET /api/health` - System health check
- `POST /api/price` - Single product pricing
- `POST /api/bulk` - Bulk pricing processing

## Demo Scenarios

### Single Product Pricing
Test individual product pricing with:
- Product name and cost inputs
- Category selection (Budget, Standard, Premium, Enterprise)
- Market segment analysis
- AI agent insights and confidence scores

### Bulk Processing
Simulate enterprise-scale operations:
- Process 10-1000 products simultaneously
- Real-time processing metrics
- Sample result visualization

### Market Analysis
Analyze market conditions:
- Segment-specific insights
- Competitive landscape analysis
- Pricing strategy recommendations

### Copilot Integration
Natural language pricing queries:
- Ask questions in plain English
- Get AI-powered recommendations
- Contextual pricing advice

## Customization

The interface can be easily customized for different industries or use cases by modifying:
- Product categories in the dropdowns
- Market segments and analysis
- Pricing calculation logic
- Visual styling and branding

## Production Deployment

For production use:
1. Configure proper API endpoints
2. Enable authentication and security
3. Set up monitoring and logging
4. Deploy to cloud infrastructure (Azure recommended)

## Enterprise Integration

This showcase can be integrated with:
- Existing ERP systems
- Microsoft 365 environments
- Azure infrastructure
- Custom enterprise applications
