#!/usr/bin/env python3
"""
Redshift Setup Guide and Connection Helper
This script helps diagnose connection issues and provides setup guidance
"""

import boto3
import json
import subprocess
import os
from botocore.exceptions import ClientError, NoCredentialsError

def check_current_aws_setup():
    """Check current AWS configuration and identity"""
    
    print("🔍 Current AWS Configuration:")
    print("-" * 40)
    
    try:
        # Check AWS credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS Credentials: Configured")
        print(f"📋 Account ID: {identity['Account']}")
        print(f"👤 User ARN: {identity['Arn']}")
        print(f"🆔 User ID: {identity['UserId']}")
        
        # Check if this looks like an Amazon internal account
        account_id = identity['Account']
        if account_id in ['809700197057', '183703362924']:
            print(f"🎯 This appears to be a compensation AWS account!")
        else:
            print(f"⚠️  This doesn't appear to be a compensation account")
            print(f"   Expected: 809700197057 (beta) or 183703362924 (prod)")
        
        return identity
        
    except NoCredentialsError:
        print("❌ No AWS credentials configured")
        return None
    except Exception as e:
        print(f"❌ Error checking AWS setup: {e}")
        return None

def check_aws_config_files():
    """Check AWS configuration files"""
    
    print(f"\n🔧 AWS Configuration Files:")
    print("-" * 40)
    
    aws_dir = os.path.expanduser("~/.aws")
    config_file = os.path.join(aws_dir, "config")
    credentials_file = os.path.join(aws_dir, "credentials")
    
    if os.path.exists(config_file):
        print(f"✅ Config file exists: {config_file}")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if 'sso' in content.lower():
                    print("🔐 SSO configuration detected")
                if 'saml' in content.lower():
                    print("🔐 SAML configuration detected")
        except Exception as e:
            print(f"❌ Error reading config: {e}")
    else:
        print(f"❌ No config file found: {config_file}")
    
    if os.path.exists(credentials_file):
        print(f"✅ Credentials file exists: {credentials_file}")
    else:
        print(f"❌ No credentials file found: {credentials_file}")

def check_environment_variables():
    """Check relevant environment variables"""
    
    print(f"\n🌍 Environment Variables:")
    print("-" * 40)
    
    env_vars = [
        'AWS_PROFILE',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_SESSION_TOKEN',
        'AWS_DEFAULT_REGION',
        'AWS_REGION'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'SECRET' in var or 'TOKEN' in var:
                # Mask sensitive values
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def test_basic_aws_services():
    """Test basic AWS service access"""
    
    print(f"\n🧪 Testing AWS Service Access:")
    print("-" * 40)
    
    # Test STS (always available)
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ STS (Security Token Service): Working")
    except Exception as e:
        print(f"❌ STS: {e}")
    
    # Test Redshift (list clusters)
    try:
        redshift = boto3.client('redshift', region_name='us-east-1')
        clusters = redshift.describe_clusters()
        print(f"✅ Redshift: Found {len(clusters['Clusters'])} clusters")
        
        for cluster in clusters['Clusters']:
            print(f"   - {cluster['ClusterIdentifier']} ({cluster['ClusterStatus']})")
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("❌ Redshift: Access denied (may need different account/role)")
        else:
            print(f"❌ Redshift: {e}")
    except Exception as e:
        print(f"❌ Redshift: {e}")
    
    # Test Redshift Data API
    try:
        redshift_data = boto3.client('redshift-data', region_name='us-east-1')
        # Just test if the client can be created
        print("✅ Redshift Data API: Client created successfully")
    except Exception as e:
        print(f"❌ Redshift Data API: {e}")

def provide_setup_guidance():
    """Provide guidance for setting up Amazon Redshift access"""
    
    print(f"\n📚 Setup Guidance for Amazon Compensation Redshift:")
    print("=" * 60)
    
    print(f"\n1️⃣ Network Requirements:")
    print("   • Must be on Amazon corporate network or VPN")
    print("   • Midway authentication required (mwinit)")
    
    print(f"\n2️⃣ LDAP Group Membership (check permissions links):")
    print("   • Read-Only Beta: https://permissions.amazon.com/a/team/ww-ops-rs-read-only-beta")
    print("   • Read-Only Prod: https://permissions.amazon.com/a/team/ww-ops-rs-read-only-prod")
    print("   • Analytics Beta: https://permissions.amazon.com/a/team/ww-ops-rs-analytics-beta")
    print("   • Analytics Prod: https://permissions.amazon.com/a/team/ww-ops-rs-analytics-prod")
    
    print(f"\n3️⃣ AWS Account Access:")
    print("   • Beta Account: 809700197057 (wage-elasticity-beta)")
    print("   • Prod Account: 183703362924 (wage-elasticity-prod)")
    
    print(f"\n4️⃣ Authentication Steps:")
    print("   1. Run: mwinit -o (Dev Desktop) or mwinit -s (Mac)")
    print("   2. Configure AWS CLI for cross-account access")
    print("   3. Use SAML federation for Redshift access")
    
    print(f"\n5️⃣ Connection Methods:")
    print("   • DataGrip with SAML plugin (GUI)")
    print("   • boto3 with assume_role (Python)")
    print("   • AWS CLI with redshift-data commands")
    
    print(f"\n6️⃣ Cluster Information:")
    print("   • Beta: beta-wwopscomp.c0g2hsdsbjbt.us-east-1.redshift.amazonaws.com")
    print("   • Prod: wwopscomp.c3kniaapvgmz.us-east-1.redshift.amazonaws.com")

def create_sample_queries():
    """Create sample SQL queries for compensation analysis"""
    
    print(f"\n📝 Sample Compensation Queries:")
    print("=" * 60)
    
    queries = {
        "explore_schemas.sql": """
-- Explore available schemas in the compensation database
SELECT schema_name, 
       schema_owner
FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
ORDER BY schema_name;
        """,
        
        "find_compensation_tables.sql": """
-- Find tables related to compensation
SELECT table_schema,
       table_name,
       table_type
FROM information_schema.tables 
WHERE (table_name ILIKE '%comp%' 
       OR table_name ILIKE '%salary%' 
       OR table_name ILIKE '%wage%'
       OR table_name ILIKE '%pay%'
       OR table_name ILIKE '%employee%'
       OR table_name ILIKE '%job%')
ORDER BY table_schema, table_name;
        """,
        
        "table_row_counts.sql": """
-- Get row counts for major tables (replace with actual table names)
SELECT 'employees' as table_name, COUNT(*) as row_count FROM employees
UNION ALL
SELECT 'compensation' as table_name, COUNT(*) as row_count FROM compensation
UNION ALL  
SELECT 'job_levels' as table_name, COUNT(*) as row_count FROM job_levels;
        """,
        
        "sample_data_exploration.sql": """
-- Sample data exploration (replace table_name with actual table)
SELECT *
FROM information_schema.columns
WHERE table_name = 'your_table_name'
ORDER BY ordinal_position;
        """
    }
    
    for filename, query in queries.items():
        with open(filename, 'w') as f:
            f.write(query.strip())
        print(f"✅ Created: {filename}")

def main():
    """Main diagnostic function"""
    
    print("🎯 Amazon Redshift Connection Diagnostic")
    print("=" * 50)
    
    # Check current setup
    identity = check_current_aws_setup()
    check_aws_config_files()
    check_environment_variables()
    test_basic_aws_services()
    
    # Provide guidance
    provide_setup_guidance()
    
    # Create sample queries
    create_sample_queries()
    
    print(f"\n🎯 Next Steps:")
    print("=" * 50)
    
    if identity:
        account_id = identity['Account']
        if account_id in ['809700197057', '183703362924']:
            print("✅ You're in a compensation AWS account!")
            print("   Try running queries directly with boto3")
        else:
            print("⚠️  You're not in a compensation account")
            print("   You'll need to assume a role or switch accounts")
    
    print(f"\n1. Ensure you're on Amazon corporate network")
    print(f"2. Run Midway authentication: mwinit -o or mwinit -s")
    print(f"3. Check LDAP group membership via the permission links above")
    print(f"4. Try the sample queries once connected")
    
    print(f"\n📁 Files created:")
    print(f"   - explore_schemas.sql")
    print(f"   - find_compensation_tables.sql") 
    print(f"   - table_row_counts.sql")
    print(f"   - sample_data_exploration.sql")

if __name__ == "__main__":
    main()