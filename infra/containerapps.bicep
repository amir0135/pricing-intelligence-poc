// Stub for Azure Container Apps deployment
param environmentName string
param location string = resourceGroup().location
output containerAppName string = 'pricing-poc-api'
