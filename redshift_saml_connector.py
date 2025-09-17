#!/usr/bin/env python3
"""
Redshift SAML Connector
Uses SAML federation to connect to Amazon compensation Redshift clusters
"""

import subprocess
import json
import os
import time
from urllib.parse import quote_plus

def create_saml_connection_config():
    """Create SAML connection configuration for DataGrip/psql"""
    
    # Connection URLs from the Amazon wiki
    connections = {
        'beta_readonly': {
            'name': 'Beta Compensation (Read-Only)',
            'url': 'jdbc:redshift:iam://beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com:5439/betawwopscomp?ssl=true&ssl_insecure=true&m_idpHost=idp-integ.federate.amazon.com&client_id=RedshiftBetaFederateSSO&iamauth=true&AutoCreate=true&dbgroups=ReadOnlySSO&idp_host=idp-integ.federate.amazon.com&use_integ=true&region=us-east-1&plugin_name=com.amazon.redshift.tools.FederateSignInCredentialsProvider&preferred_role=arn:aws:iam::809700197057:role/Federate_SAML_ROLE_Beta&clusterID=beta-wwopscomp',
            'account': '809700197057',
            'cluster': 'beta-wwopscomp',
            'database': 'betawwopscomp'
        },
        'prod_readonly': {
            'name': 'Production Compensation (Read-Only)',
            'url': 'jdbc:redshift:iam://wwopscomp.c3kniaapvgmz.us-east-1.redshift.amazonaws.com:5439/wwopscomp?ssl=true&ssl_insecure=true&m_idpHost=idp.federate.amazon.com&client_id=RedshiftProdFederateSSO&iamauth=true&AutoCreate=true&dbgroups=ReadOnlySSO&idp_host=idp.federate.amazon.com&use_integ=true&region=us-east-1&plugin_name=com.amazon.redshift.tools.FederateSignInCredentialsProvider&preferred_role=arn:aws:iam::183703362924:role/Federate_SAML_ROLE_Prod&clusterID=wwopscomp',
            'account': '183703362924',
            'cluster': 'wwopscomp',
            'database': 'wwopscomp'
        },
        'beta_analytics': {
            'name': 'Beta Compensation (Analytics)',
            'url': 'jdbc:redshift:iam://beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com:5439/betawwopscomp?ssl=true&ssl_insecure=true&m_idpHost=idp-integ.federate.amazon.com&client_id=RedshiftBetaFederateAnalyticsSSO&iamauth=true&AutoCreate=true&dbgroups=analyticsso&idp_host=idp-integ.federate.amazon.com&use_integ=true&region=us-east-1&plugin_name=com.amazon.redshift.tools.FederateSignInCredentialsProvider&preferred_role=arn:aws:iam::809700197057:role/Federate_SAML_Analytics_Role_Beta&clusterID=beta-wwopscomp',
            'account': '809700197057',
            'cluster': 'beta-wwopscomp',
            'database': 'betawwopscomp'
        }
    }
    
    return connections

def test_midway_authentication():
    """Test if Midway authentication is working"""
    
    print("🔐 Testing Midway Authentication:")
    print("-" * 40)
    
    try:
        # Try to get Midway status
        result = subprocess.run(['mwinit', '-s'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0:
            print("✅ Midway authentication successful")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Midway authentication failed")
            if result.stderr:
                print(f"Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏳ Midway authentication timed out")
        print("💡 This might mean you need to re-authenticate")
        return False
    except FileNotFoundError:
        print("❌ mwinit command not found")
        return False
    except Exception as e:
        print(f"❌ Error testing Midway: {e}")
        return False

def create_datagrip_instructions():
    """Create instructions for DataGrip setup"""
    
    instructions = """
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
"""
    
    with open('DataGrip_Redshift_Setup.md', 'w') as f:
        f.write(instructions)
    
    print("✅ Created DataGrip_Redshift_Setup.md")

def create_python_connection_example():
    """Create Python connection example using psycopg2"""
    
    python_example = '''#!/usr/bin/env python3
"""
Python Redshift Connection Example
This shows how to connect to Redshift using psycopg2 with SAML authentication
"""

import psycopg2
import os
import subprocess

def get_saml_credentials():
    """Get SAML credentials for Redshift connection"""
    
    # This would typically involve calling the SAML federation endpoint
    # For now, this is a placeholder showing the concept
    
    print("🔐 SAML authentication would happen here")
    print("💡 In practice, you'd use the JDBC driver with SAML plugin")
    
    return None

def connect_to_redshift_beta():
    """Connect to Beta Redshift cluster"""
    
    # Connection parameters for Beta cluster
    conn_params = {
        'host': 'beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com',
        'port': 5439,
        'database': 'betawwopscomp',
        'user': 'your_username',  # This would come from SAML
        'password': 'your_saml_token'  # This would come from SAML
    }
    
    try:
        # Note: This won't work without proper SAML authentication
        # This is just showing the connection pattern
        conn = psycopg2.connect(**conn_params)
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database();")
        result = cursor.fetchone()
        
        print(f"Connected as: {result[0]} to database: {result[1]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def main():
    """Main function"""
    
    print("🎯 Python Redshift Connection Example")
    print("=" * 50)
    
    print("⚠️  Note: This example shows the connection pattern")
    print("   For actual connections, use DataGrip with SAML plugin")
    print("   or AWS CLI with redshift-data commands")
    
    # Test SAML credentials
    creds = get_saml_credentials()
    
    if creds:
        connect_to_redshift_beta()
    else:
        print("❌ SAML authentication not implemented")
        print("💡 Use DataGrip with SAML plugin for actual connections")

if __name__ == "__main__":
    main()
'''
    
    with open('python_redshift_example.py', 'w') as f:
        f.write(python_example)
    
    print("✅ Created python_redshift_example.py")

def main():
    """Main function"""
    
    print("🎯 Redshift SAML Connection Setup")
    print("=" * 50)
    
    # Test Midway authentication
    midway_ok = test_midway_authentication()
    
    # Get connection configurations
    connections = create_saml_connection_config()
    
    print(f"\n📊 Available Redshift Connections:")
    print("-" * 40)
    
    for key, conn in connections.items():
        print(f"\n{conn['name']}:")
        print(f"  Account: {conn['account']}")
        print(f"  Cluster: {conn['cluster']}")
        print(f"  Database: {conn['database']}")
    
    # Create setup instructions
    create_datagrip_instructions()
    create_python_connection_example()
    
    print(f"\n🎯 Next Steps:")
    print("=" * 50)
    
    if midway_ok:
        print("✅ Midway authentication is working")
        print("1. Follow DataGrip setup instructions in DataGrip_Redshift_Setup.md")
        print("2. Download required JDBC drivers and SAML plugin")
        print("3. Configure DataGrip with the connection URLs")
        print("4. Test connection to Beta cluster first")
    else:
        print("❌ Midway authentication needs attention")
        print("1. Run: mwinit -s")
        print("2. Ensure you're on Amazon VPN")
        print("3. Verify LDAP group membership")
        print("4. Then follow DataGrip setup instructions")
    
    print(f"\n📁 Files Created:")
    print("- DataGrip_Redshift_Setup.md (Complete setup guide)")
    print("- python_redshift_example.py (Python connection example)")
    
    print(f"\n💡 Alternative: Once DataGrip is working,")
    print("   I can help you write and analyze SQL queries!")

if __name__ == "__main__":
    main()