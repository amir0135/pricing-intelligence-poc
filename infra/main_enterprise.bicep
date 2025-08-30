// Enterprise Multi-Agent Pricing Intelligence Infrastructure
// Scalable Azure deployment for large customer environments

@description('Environment name (dev, staging, prod)')
param environmentName string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Resource prefix')
param resourcePrefix string = 'pricing-intel'

@description('Enable high availability (zone redundancy)')
param enableHighAvailability bool = (environmentName == 'prod')

@description('Enable auto-scaling')
param enableAutoScaling bool = true

@description('Minimum replica count')
param minReplicas int = (environmentName == 'prod') ? 3 : 1

@description('Maximum replica count')
param maxReplicas int = (environmentName == 'prod') ? 100 : 10

@description('Enable monitoring and alerting')
param enableMonitoring bool = true

@description('Enable backup and disaster recovery')
param enableBackup bool = (environmentName == 'prod')

@description('Application insights sampling rate')
param samplingRate int = (environmentName == 'prod') ? 10 : 100

@description('Database tier')
param databaseTier string = (environmentName == 'prod') ? 'Premium' : 'Standard'

@description('Container registry SKU')
param acrSku string = (environmentName == 'prod') ? 'Premium' : 'Standard'

@description('SQL Administrator password')
@secure()
param sqlAdminPassword string

// Variables
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 6)
var resourceName = '${resourcePrefix}-${environmentName}-${uniqueSuffix}'
var acrName = length('${resourcePrefix}${environmentName}${uniqueSuffix}acr') > 5 ? '${resourcePrefix}${environmentName}${uniqueSuffix}acr' : 'pricingacr${uniqueSuffix}'

// Log Analytics Workspace for monitoring
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${resourceName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: (environmentName == 'prod') ? 365 : 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
    'azd-env-name': environmentName
  }
}

// Application Insights for application monitoring
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = if (enableMonitoring) {
  name: '${resourceName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    SamplingPercentage: samplingRate
    RetentionInDays: (environmentName == 'prod') ? 365 : 30
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Key Vault for secrets management
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${resourceName}-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: (environmentName == 'prod') ? 90 : 7
    enablePurgeProtection: (environmentName == 'prod') ? true : false
    publicNetworkAccess: 'Enabled'
    accessPolicies: []
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Container Registry for application images
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: false
    policies: {
      quarantinePolicy: {
        status: 'enabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'enabled'
      }
      retentionPolicy: {
        days: (environmentName == 'prod') ? 30 : 7
        status: 'enabled'
      }
    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: enableHighAvailability ? 'Enabled' : 'Disabled'
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// User Assigned Managed Identity
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${resourceName}-identity'
  location: location
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Key Vault access policy for managed identity
resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  name: 'add'
  parent: keyVault
  properties: {
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: userAssignedIdentity.properties.principalId
        permissions: {
          secrets: ['Get', 'List']
          certificates: ['Get', 'List']
          keys: ['Get', 'List']
        }
      }
    ]
  }
}

// ACR pull role assignment for managed identity
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, userAssignedIdentity.id, 'AcrPull')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: userAssignedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// Azure SQL Database for enterprise data storage
resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: '${resourceName}-sql'
  location: location
  properties: {
    administratorLogin: 'sqladmin'
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  name: 'pricing-intelligence-db'
  parent: sqlServer
  location: location
  sku: {
    name: (environmentName == 'prod') ? 'S3' : 'S1'
    tier: databaseTier
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: (environmentName == 'prod') ? 1099511627776 : 268435456000 // 1TB for prod, 250GB for others
    catalogCollation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: enableHighAvailability
    readScale: (environmentName == 'prod') ? 'Enabled' : 'Disabled'
    requestedBackupStorageRedundancy: enableBackup ? 'Geo' : 'Local'
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Redis Cache for high-performance caching
resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: '${resourceName}-redis'
  location: location
  properties: {
    sku: {
      name: (environmentName == 'prod') ? 'Premium' : 'Standard'
      family: (environmentName == 'prod') ? 'P' : 'C'
      capacity: (environmentName == 'prod') ? 1 : 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    redisConfiguration: {
      'maxmemory-policy': 'allkeys-lru'
    }
    redisVersion: '6'
    replicasPerMaster: enableHighAvailability ? 1 : 0
    replicasPerPrimary: enableHighAvailability ? 1 : 0
    shardCount: (environmentName == 'prod') ? 3 : 1
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${resourceName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    zoneRedundant: enableHighAvailability
    infrastructureResourceGroup: '${resourceName}-infra-rg'
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
      {
        name: 'Dedicated-D4'
        workloadProfileType: 'D4'
        minimumCount: enableHighAvailability ? 1 : 0
        maximumCount: (environmentName == 'prod') ? 10 : 3
      }
    ]
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
    'azd-env-name': environmentName
  }
}

// Pricing Orchestrator Container App
resource orchestratorApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${resourceName}-orchestrator'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    workloadProfileName: (environmentName == 'prod') ? 'Dedicated-D4' : 'Consumption'
    configuration: {
      activeRevisionsMode: 'Multiple'
      maxInactiveRevisions: 5
      ingress: {
        external: true
        targetPort: 8000
        allowInsecure: false
        traffic: [
          {
            weight: 100
            latestRevision: true
          }
        ]
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
          allowedHeaders: ['*']
        }
      }
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: userAssignedIdentity.id
        }
      ]
      secrets: [
        {
          name: 'database-connection'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/database-connection'
          identity: userAssignedIdentity.id
        }
        {
          name: 'redis-connection'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/redis-connection'
          identity: userAssignedIdentity.id
        }
        {
          name: 'app-insights-key'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/app-insights-key'
          identity: userAssignedIdentity.id
        }
      ]
    }
    template: {
      revisionSuffix: 'v${substring(uniqueString(deployment().name), 0, 6)}'
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: enableAutoScaling ? [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
          {
            name: 'cpu-scale'
            custom: {
              type: 'cpu'
              metadata: {
                type: 'Utilization'
                value: '70'
              }
            }
          }
          {
            name: 'memory-scale'
            custom: {
              type: 'memory'
              metadata: {
                type: 'Utilization'
                value: '80'
              }
            }
          }
        ] : []
      }
      containers: [
        {
          name: 'pricing-orchestrator'
          image: '${containerRegistry.properties.loginServer}/pricing-orchestrator:latest'
          resources: {
            cpu: json((environmentName == 'prod') ? '2.0' : '1.0')
            memory: (environmentName == 'prod') ? '4Gi' : '2Gi'
          }
          env: [
            {
              name: 'ENVIRONMENT'
              value: environmentName
            }
            {
              name: 'DATABASE_CONNECTION'
              secretRef: 'database-connection'
            }
            {
              name: 'REDIS_CONNECTION'
              secretRef: 'redis-connection'
            }
            {
              name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
              secretRef: 'app-insights-key'
            }
            {
              name: 'LOG_LEVEL'
              value: (environmentName == 'prod') ? 'INFO' : 'DEBUG'
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 30
              periodSeconds: 10
              timeoutSeconds: 5
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
              }
              initialDelaySeconds: 10
              periodSeconds: 5
              timeoutSeconds: 3
              failureThreshold: 3
            }
          ]
        }
      ]
    }
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
  dependsOn: [
    acrPullRoleAssignment
    keyVaultAccessPolicy
  ]
}

// API Management for enterprise API gateway (prod only)
resource apiManagement 'Microsoft.ApiManagement/service@2023-05-01-preview' = if (environmentName == 'prod') {
  name: '${resourceName}-apim'
  location: location
  sku: {
    name: 'Developer'
    capacity: 1
  }
  properties: {
    publisherEmail: 'admin@company.com'
    publisherName: 'Pricing Intelligence Team'
    notificationSenderEmail: 'noreply@company.com'
    publicNetworkAccess: 'Enabled'
    virtualNetworkType: 'None'
    customProperties: {
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls11': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Protocols.Tls10': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls11': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Tls10': 'false'
      'Microsoft.WindowsAzure.ApiManagement.Gateway.Security.Backend.Protocols.Ssl30': 'false'
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  tags: {
    Environment: environmentName
    Application: 'pricing-intelligence'
  }
}

// Store connection strings and keys in Key Vault
resource databaseConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'database-connection'
  parent: keyVault
  properties: {
    value: 'Server=${sqlServer.properties.fullyQualifiedDomainName};Database=${sqlDatabase.name};Authentication=Active Directory Managed Identity;User Id=${userAssignedIdentity.properties.clientId};'
  }
}

resource redisConnectionSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: 'redis-connection'
  parent: keyVault
  properties: {
    value: '${redisCache.properties.hostName}:${redisCache.properties.sslPort},password=${redisCache.listKeys().primaryKey},ssl=True,abortConnect=False'
  }
}

resource appInsightsKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (enableMonitoring) {
  name: 'app-insights-key'
  parent: keyVault
  properties: {
    value: 'placeholder-key-will-be-set-by-deployment'
  }
}

// Outputs for reference
output resourceGroupName string = resourceGroup().name
output containerRegistryName string = containerRegistry.name
output containerRegistryUrl string = containerRegistry.properties.loginServer
output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output orchestratorUrl string = 'https://${orchestratorApp.properties.configuration.ingress.fqdn}'
output sqlServerName string = sqlServer.name
output sqlDatabaseName string = sqlDatabase.name
output redisCacheName string = redisCache.name
output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId
output managedIdentityClientId string = userAssignedIdentity.properties.clientId
