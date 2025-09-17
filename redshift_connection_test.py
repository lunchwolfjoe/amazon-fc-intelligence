#!/usr/bin/env python3
"""
Redshift Connection Test using boto3
This script tests connection to Amazon's internal Redshift clusters
"""

import boto3
import json
import time
from botocore.exceptions import ClientError, NoCredentialsError

def test_aws_credentials():
    """Test if AWS credentials are properly configured"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS Credentials configured successfully")
        print(f"Account ID: {identity['Account']}")
        print(f"User ARN: {identity['Arn']}")
        print(f"User ID: {identity['UserId']}")
        return True
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("Run: aws configure")
        return False
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False

def list_redshift_clusters():
    """List available Redshift clusters"""
    try:
        redshift = boto3.client('redshift', region_name='us-east-1')
        clusters = redshift.describe_clusters()
        
        print("\n📊 Available Redshift Clusters:")
        for cluster in clusters['Clusters']:
            print(f"  - Cluster: {cluster['ClusterIdentifier']}")
            print(f"    Status: {cluster['ClusterStatus']}")
            print(f"    Endpoint: {cluster['Endpoint']['Address']}")
            print(f"    Database: {cluster['DBName']}")
            print()
        return clusters['Clusters']
    except Exception as e:
        print(f"❌ Error listing clusters: {e}")
        return []

def test_redshift_data_api(cluster_id, database_name):
    """Test Redshift Data API connection"""
    try:
        redshift_data = boto3.client('redshift-data', region_name='us-east-1')
        
        # Simple test query
        response = redshift_data.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database_name,
            Sql="SELECT current_user, current_database(), version();"
        )
        
        query_id = response['Id']
        print(f"✅ Query submitted successfully. Query ID: {query_id}")
        
        # Wait for query to complete
        print("⏳ Waiting for query to complete...")
        while True:
            status_response = redshift_data.describe_statement(Id=query_id)
            status = status_response['Status']
            
            if status == 'FINISHED':
                print("✅ Query completed successfully")
                break
            elif status == 'FAILED':
                print(f"❌ Query failed: {status_response.get('Error', 'Unknown error')}")
                return False
            elif status in ['SUBMITTED', 'PICKED', 'STARTED']:
                print(f"⏳ Query status: {status}")
                time.sleep(2)
            else:
                print(f"❓ Unknown status: {status}")
                time.sleep(2)
        
        # Get query results
        result = redshift_data.get_statement_result(Id=query_id)
        
        print("\n📋 Query Results:")
        for record in result['Records']:
            values = [field.get('stringValue', field.get('longValue', field.get('booleanValue', 'NULL'))) 
                     for field in record]
            print(f"  {values}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with Redshift Data API: {e}")
        return False

def test_compensation_clusters():
    """Test connection to specific compensation clusters"""
    
    # Compensation cluster configurations from the wiki
    clusters = [
        {
            'name': 'beta-wwopscomp',
            'database': 'betawwopscomp',
            'description': 'Beta compensation cluster'
        },
        {
            'name': 'wwopscomp', 
            'database': 'wwopscomp',
            'description': 'Production compensation cluster'
        }
    ]
    
    print("\n🎯 Testing Compensation Clusters:")
    
    for cluster in clusters:
        print(f"\n--- Testing {cluster['description']} ---")
        print(f"Cluster: {cluster['name']}")
        print(f"Database: {cluster['database']}")
        
        success = test_redshift_data_api(cluster['name'], cluster['database'])
        if success:
            print(f"✅ Successfully connected to {cluster['name']}")
            return cluster  # Return first successful connection
        else:
            print(f"❌ Failed to connect to {cluster['name']}")
    
    return None

def run_sample_queries(cluster_config):
    """Run some sample queries to explore the database"""
    
    if not cluster_config:
        print("❌ No cluster configuration provided")
        return
    
    redshift_data = boto3.client('redshift-data', region_name='us-east-1')
    
    sample_queries = [
        {
            'name': 'List Schemas',
            'sql': "SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;"
        },
        {
            'name': 'List Tables in Public Schema',
            'sql': "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
        },
        {
            'name': 'Database Size',
            'sql': "SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;"
        }
    ]
    
    print(f"\n🔍 Running Sample Queries on {cluster_config['name']}:")
    
    for query in sample_queries:
        print(f"\n--- {query['name']} ---")
        try:
            response = redshift_data.execute_statement(
                ClusterIdentifier=cluster_config['name'],
                Database=cluster_config['database'],
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
                
                # Print column headers if available
                if 'ColumnMetadata' in result:
                    headers = [col['name'] for col in result['ColumnMetadata']]
                    print(f"Columns: {headers}")
                
                # Print results
                for record in result['Records']:
                    values = [field.get('stringValue', field.get('longValue', field.get('booleanValue', 'NULL'))) 
                             for field in record]
                    print(f"  {values}")
                    
        except Exception as e:
            print(f"❌ Error running query '{query['name']}': {e}")

def main():
    """Main function to test Redshift connection"""
    
    print("🚀 Amazon Redshift Connection Test")
    print("=" * 50)
    
    # Step 1: Test AWS credentials
    if not test_aws_credentials():
        print("\n💡 To configure AWS credentials:")
        print("1. Run: aws configure")
        print("2. Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("3. Or use AWS SSO: aws sso login")
        return
    
    # Step 2: List available clusters
    print("\n" + "=" * 50)
    clusters = list_redshift_clusters()
    
    # Step 3: Test compensation-specific clusters
    print("\n" + "=" * 50)
    successful_cluster = test_compensation_clusters()
    
    # Step 4: Run sample queries if connection successful
    if successful_cluster:
        print("\n" + "=" * 50)
        run_sample_queries(successful_cluster)
        
        print(f"\n✅ Connection test completed successfully!")
        print(f"You can now query the {successful_cluster['name']} cluster")
        
    else:
        print("\n❌ Could not connect to any compensation clusters")
        print("\n💡 Troubleshooting steps:")
        print("1. Ensure you're on Amazon VPN or corporate network")
        print("2. Run: mwinit -o (or mwinit -s on Mac)")
        print("3. Check LDAP group membership for Redshift access")
        print("4. Verify AWS credentials are configured for the right account")

if __name__ == "__main__":
    main()