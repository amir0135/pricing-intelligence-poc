# Copilot for Microsoft 365 Plugin

This folder contains the plugin files to integrate pricing intelligence into Microsoft 365 Copilot.

## Files
- `manifest.json`: Plugin manifest with actions and authentication
- `api-reference.yaml`: OpenAPI specification (mirrors `../api/openapi.yaml`)

## How to Import into Copilot Studio

1. **Create a new plugin** in Copilot Studio
2. **Choose "OpenAPI"** as the plugin type
3. **Upload** the `api-reference.yaml` file
4. **Configure OAuth 2.0** authentication:
   - Authorization URL: `https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/authorize`
   - Token URL: `https://login.microsoftonline.com/{tenantId}/oauth2/v2.0/token`
   - Scope: `api://pricing-poc/user_impersonation`
5. **Test the actions**:
   - GetPriceRecommendation
   - ScorePrice
   - GetWinCurve
   - SubmitFeedback

## Example Copilot Queries

Once imported, users can ask:
- "What's the recommended price for SKU-001 for customer C-100 with quantity 10 in Germany?"
- "Score a price of $120 for SKU-001 to customer C-100"
- "Show me the win curve for SKU-002 to customer C-200"
- "Why is the target price lower in France this month?"

## Multi-Agent Intelligence

The plugin leverages our multi-model agent architecture:
- **Rules Agent**: Enforces business policies
- **WinRate Agent**: ML-powered win probability prediction  
- **Elasticity Agent**: Economic price sensitivity modeling
- **Explainer Agent**: Natural language explanations
- **Orchestrator**: Coordinates all agents for optimal recommendations

This provides salespeople with transparent, explainable AI recommendations directly in their Microsoft 365 workflow.
