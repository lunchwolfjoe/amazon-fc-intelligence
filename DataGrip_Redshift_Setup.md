
# DataGrip Setup Instructions for Amazon Redshift

## Prerequisites
1. ✅ You're on Amazon VPN
2. ✅ You've run `mwinit -s` successfully  
3. ✅ You have LDAP group access
4. ⬜ Download DataGrip from JetBrains
5. ⬜ Download Redshift JDBC Driver
6. ⬜ Download SAML Plugin

## Driver Setup Steps

### 1. Download Required Files
- **Redshift Driver**: RedshiftJDBC42-1.2.43.1067.jar
- **SAML Plugin**: RedshiftFederateSamlPlugin-1.0.1-bundle.jar
- Available from: https://drive.corp.amazon.com/documents/ascottr@/Shared_files/

### 2. Configure DataGrip Driver
1. Open DataGrip
2. Click + → Driver
3. Name: "Redshift SSO"
4. Add both JAR files to Driver Files
5. Select Driver Class: `com.amazon.redshift.jdbc.Driver`

### 3. Create Data Source
1. Click + → Data Source → "Redshift SSO"
2. Paste one of the connection URLs below
3. Test Connection

## Connection URLs

### Beta Cluster (Read-Only)
```
jdbc:redshift:iam://beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com:5439/betawwopscomp?ssl=true&ssl_insecure=true&m_idpHost=idp-integ.federate.amazon.com&client_id=RedshiftBetaFederateSSO&iamauth=true&AutoCreate=true&dbgroups=ReadOnlySSO&idp_host=idp-integ.federate.amazon.com&use_integ=true&region=us-east-1&plugin_name=com.amazon.redshift.tools.FederateSignInCredentialsProvider&preferred_role=arn:aws:iam::809700197057:role/Federate_SAML_ROLE_Beta&clusterID=beta-wwopscomp
```

### Production Cluster (Read-Only)  
```
jdbc:redshift:iam://wwopscomp.c3kniaapvgmz.us-east-1.redshift.amazonaws.com:5439/wwopscomp?ssl=true&ssl_insecure=true&m_idpHost=idp.federate.amazon.com&client_id=RedshiftProdFederateSSO&iamauth=true&AutoCreate=true&dbgroups=ReadOnlySSO&idp_host=idp.federate.amazon.com&use_integ=true&region=us-east-1&plugin_name=com.amazon.redshift.tools.FederateSignInCredentialsProvider&preferred_role=arn:aws:iam::183703362924:role/Federate_SAML_ROLE_Prod&clusterID=wwopscomp
```

## Troubleshooting

### Common Issues
1. **"Failed to retrieve SAMLAssertion"**
   - Run `mwinit -s` again
   - Ensure you're on Amazon VPN

2. **"Access Denied"**
   - Check LDAP group membership
   - Verify you have the right permissions

3. **"Connection Timeout"**
   - Verify VPN connection
   - Check if you're on corporate network

### LDAP Groups Required
- Read-Only Beta: ww-ops-rs-read-only-beta
- Read-Only Prod: ww-ops-rs-read-only-prod
- Analytics Beta: ww-ops-rs-analytics-beta
- Analytics Prod: ww-ops-rs-analytics-prod

## Once Connected
You can run SQL queries directly in DataGrip:

```sql
-- Test connection
SELECT current_user, current_database(), version();

-- Explore schemas
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog');

-- Find compensation tables
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_name ILIKE '%comp%' OR table_name ILIKE '%salary%';
```
