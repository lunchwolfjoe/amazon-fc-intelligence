#!/usr/bin/env python3
"""
Redshift SSO Connection for Amazon Compensation Clusters
This script handles cross-account access to compensation Redshift clusters
"""

import boto3
import json
import time
import subprocess
import os
from botocore.exceptions import ClientError, NoCredentialsError

def check_midway_auth():
    """Check if Midway authentication is active"""
    try:
        # Check if mwinit has been run recently
        result = subprocess.run(['mwinit', '-s'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Midway authentication appears to be active")
            return True
        else:
            print("❌ Midway authentication may not be active")
            print("💡 Run: mwinit -o (Dev Desktop) or mwinit -s (Mac)")
            return False
    except subprocess.TimeoutExpired:
        print("⏳ Midway command timed out - you may need to authenticate")
        return False
    except FileNotFoundError:
        print("❌ mwinit command not found")
        print("💡 Ensure you're on Amazon corporate network with Midway installed")
        return False
    except Exception as e:
        print(f"❓ Could not check Midway status: {e}")
        return False

def assume_compensation_role(target_account, role_name):
    """Assume role in the compensation AWS account"""
    try:
        sts = boto3.client('sts')
        
        # Construct the role ARN based on the account and role
        role_arn = f"arn:aws:iam::{target_account}:role/{role_name}"
        
        print(f"🔄 Attempting to assume role: {role_arn}")
        
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='compensation-analysis-session'
        )
        
        credentials = response['Credentials']
        
        # Create new session with assumed role credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        print("✅ Successfully assumed compensation role")
        return session
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print(f"❌ Access denied assuming role: {role_arn}")
            print("💡 Check LDAP group membership for compensation access")
        else:
            print(f"❌ Error assuming role: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error assuming role: {e}")
        return None

def test_redshift_data_api_with_session(session, cluster_id, database_name, region='us-east-1'):
    """Test Redshift Data API with specific session"""
    try:
        redshift_data = session.client('redshift-data', region_name=region)
        
        print(f"🔍 Testing connection to cluster: {cluster_id}")
        print(f"📊 Database: {database_name}")
        
        # Simple test query
        response = redshift_data.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database_name,
            Sql="SELECT current_user, current_database(), current_timestamp;"
        )
        
        query_id = response['Id']
        print(f"✅ Query submitted. ID: {query_id}")
        
        # Wait for query completion
        max_wait = 30  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status_response = redshift_data.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                print("✅ Query completed successfully")
                
                # Get results
                result = redshift_data.get_statement_result(Id=query_id)
                
                print("\n📋 Connection Test Results:")
                if 'ColumnMetadata' in result:
                    headers = [col['name'] for col in result['ColumnMetadata']]
                    print(f"Columns: {headers}")
                
                for record in result['Records']:
                    values = []
                    for field in record:
                        if 'stringValue' in field:
                            values.append(field['stringValue'])
                        elif 'longValue' in field:
                            values.append(str(field['longValue']))
                        elif 'timestampValue' in field:
                            values.append(str(field['timestampValue']))
                        else:
                            values.append('NULL')
                    print(f"  {values}")
                
                return True
                
            elif status == 'FAILED':
                error_msg = status_response.get('Error', 'Unknown error')
                print(f"❌ Query failed: {error_msg}")
                return False
                
            elif status in ['SUBMITTED', 'PICKED', 'STARTED']:
                print(f"⏳ Query status: {status}")
                time.sleep(2)
                wait_time += 2
            else:
                print(f"❓ Unknown status: {status}")
                time.sleep(2)
                wait_time += 2
        
        print("⏰ Query timed out")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print(f"❌ Access denied to cluster {cluster_id}")
            print("💡 Check LDAP group membership and cluster permissions")
        elif error_code == 'ClusterNotFound':
            print(f"❌ Cluster {cluster_id} not found in this account/region")
        else:
            print(f"❌ AWS Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def explore_compensation_data(session, cluster_id, database_name):
    """Explore available schemas and tables in compensation database"""
    
    redshift_data = session.client('redshift-data', region_name='us-east-1')
    
    queries = [
        {
            'name': 'Available Schemas',
            'sql': """
                SELECT schema_name, 
                       schema_owner
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name;
            """
        },
        {
            'name': 'Tables in Public Schema',
            'sql': """
                SELECT table_name, 
                       table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
                LIMIT 20;
            """
        },
        {
            'name': 'Sample Compensation Tables',
            'sql': """
                SELECT table_schema,
                       table_name
                FROM information_schema.tables 
                WHERE (table_name ILIKE '%comp%' 
                       OR table_name ILIKE '%salary%' 
                       OR table_name ILIKE '%wage%'
                       OR table_name ILIKE '%pay%')
                ORDER BY table_schema, table_name
                LIMIT 10;
            """
        }
    ]
    
    print(f"\n🔍 Exploring {cluster_id} Database Structure:")
    
    for query in queries:
        print(f"\n--- {query['name']} ---")
        
        try:
            response = redshift_data.execute_statement(
                ClusterIdentifier=cluster_id,
                Database=database_name,
                Sql=query['sql']
            )
            
            query_id = response['Id']
            
            # Wait for completion
            while True:
                status_response = redshift_data.describe_statement(Id=query_id)
                if status_response['Status'] == 'FINISHED':
                    break
                elif status_response['Status'] == 'FAILED':
                    print(f"❌ Query failed: {status_response.get('Error', 'Unknown error')}")
                    break
                time.sleep(1)
            
            if status_response['Status'] == 'FINISHED':
                result = redshift_data.get_statement_result(Id=query_id)
                
                # Print results
                if result['Records']:
                    for record in result['Records']:
                        values = []
                        for field in record:
                            if 'stringValue' in field:
                                values.append(field['stringValue'])
                            elif 'longValue' in field:
                                values.append(str(field['longValue']))
                            else:
                                values.append('NULL')
                        print(f"  {values}")
                else:
                    print("  No results found")
                    
        except Exception as e:
            print(f"❌ Error running query: {e}")

def main():
    """Main function to test compensation Redshift access"""
    
    print("🎯 Amazon Compensation Redshift Connection Test")
    print("=" * 60)
    
    # Check Midway authentication
    print("\n1️⃣ Checking Midway Authentication:")
    if not check_midway_auth():
        return
    
    # Test different compensation accounts and roles
    compensation_configs = [
        {
            'name': 'Beta Compensation Cluster',
            'account': '809700197057',  # wage-elasticity-beta
            'cluster': 'beta-wwopscomp',
            'database': 'betawwopscomp',
            'roles': [
                'Federate_SAML_ROLE_Beta',
                'Federate_SAML_Analytics_Role_Beta',
                'Federate_SAML_Admin_Role_Beta'
            ]
        },
        {
            'name': 'Production Compensation Cluster', 
            'account': '183703362924',  # wage-elasticity-prod
            'cluster': 'wwopscomp',
            'database': 'wwopscomp',
            'roles': [
                'Federate_SAML_ROLE_Prod',
                'Federate_SAML_Analytics_Role_Prod',
                'Federate_SAML_Admin_Role_Prod'
            ]
        }
    ]
    
    successful_connection = None
    
    for config in compensation_configs:
        print(f"\n2️⃣ Testing {config['name']}:")
        print(f"Account: {config['account']}")
        print(f"Cluster: {config['cluster']}")
        
        # Try different roles in order of increasing permissions
        for role in config['roles']:
            print(f"\n🔐 Trying role: {role}")
            
            session = assume_compensation_role(config['account'], role)
            if session:
                success = test_redshift_data_api_with_session(
                    session, 
                    config['cluster'], 
                    config['database']
                )
                
                if success:
                    print(f"✅ Successfully connected with role: {role}")
                    successful_connection = (session, config)
                    break
                else:
                    print(f"❌ Connection failed with role: {role}")
            else:
                print(f"❌ Could not assume role: {role}")
        
        if successful_connection:
            break
    
    # If we have a successful connection, explore the database
    if successful_connection:
        session, config = successful_connection
        print(f"\n3️⃣ Exploring Database Structure:")
        explore_compensation_data(session, config['cluster'], config['database'])
        
        print(f"\n✅ Connection test completed successfully!")
        print(f"Connected to: {config['name']}")
        print(f"You can now query compensation data!")
        
    else:
        print(f"\n❌ Could not connect to any compensation clusters")
        print(f"\n💡 Troubleshooting:")
        print(f"1. Ensure mwinit authentication: mwinit -o or mwinit -s")
        print(f"2. Check LDAP group membership:")
        print(f"   - ww-ops-rs-read-only-beta")
        print(f"   - ww-ops-rs-read-only-prod") 
        print(f"   - ww-ops-rs-analytics-beta")
        print(f"   - ww-ops-rs-analytics-prod")
        print(f"3. Verify you're on Amazon corporate network/VPN")

if __name__ == "__main__":
    main()