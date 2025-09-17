#!/usr/bin/env python3
"""
Automated AWS Amplify Deployment Script
One-click deployment to AWS with real data persistence
"""

import subprocess
import json
import os
import time
from datetime import datetime

class AWSAmplifyDeployer:
    def __init__(self):
        self.app_name = "amazon-fc-intelligence"
        self.region = "us-east-1"
        self.table_name = "amazon-fc-posts"
        
    def check_prerequisites(self):
        """Check if required tools are installed."""
        print("🔍 Checking prerequisites...")
        
        required_tools = [
            ("aws", "AWS CLI"),
            ("git", "Git")
        ]
        
        for tool, name in required_tools:
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
                print(f"✅ {name} is installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ {name} is not installed or not in PATH")
                return False
        
        # Check AWS credentials
        try:
            result = subprocess.run(["aws", "sts", "get-caller-identity"], 
                                  capture_output=True, text=True, check=True)
            identity = json.loads(result.stdout)
            print(f"✅ AWS credentials configured for account: {identity.get('Account')}")
            return True
        except subprocess.CalledProcessError:
            print("❌ AWS credentials not configured. Run 'aws configure' first.")
            return False
    
    def create_dynamodb_table(self):
        """Create DynamoDB table for data storage."""
        print("🗄️ Creating DynamoDB table...")
        
        table_config = {
            "TableName": self.table_name,
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "created_utc", "KeyType": "RANGE"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "created_utc", "AttributeType": "N"},
                {"AttributeName": "subject_area", "AttributeType": "S"}
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "subject-area-index",
                    "KeySchema": [
                        {"AttributeName": "subject_area", "KeyType": "HASH"},
                        {"AttributeName": "created_utc", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            "BillingMode": "PAY_PER_REQUEST",
            "Tags": [
                {"Key": "Project", "Value": "AmazonFCIntelligence"},
                {"Key": "Environment", "Value": "Production"}
            ]
        }
        
        try:
            # Check if table exists
            subprocess.run([
                "aws", "dynamodb", "describe-table",
                "--table-name", self.table_name,
                "--region", self.region
            ], capture_output=True, check=True)
            print(f"✅ DynamoDB table '{self.table_name}' already exists")
            return True
            
        except subprocess.CalledProcessError:
            # Table doesn't exist, create it
            try:
                with open("table_config.json", "w") as f:
                    json.dump(table_config, f, indent=2)
                
                subprocess.run([
                    "aws", "dynamodb", "create-table",
                    "--cli-input-json", f"file://table_config.json",
                    "--region", self.region
                ], check=True)
                
                print(f"✅ Created DynamoDB table '{self.table_name}'")
                print("⏳ Waiting for table to become active...")
                
                # Wait for table to be active
                subprocess.run([
                    "aws", "dynamodb", "wait", "table-exists",
                    "--table-name", self.table_name,
                    "--region", self.region
                ], check=True)
                
                os.remove("table_config.json")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to create DynamoDB table: {e}")
                return False
    
    def create_iam_role(self):
        """Create IAM role for Amplify with DynamoDB permissions."""
        print("🔐 Creating IAM role...")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "amplify.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem"
                    ],
                    "Resource": [
                        f"arn:aws:dynamodb:{self.region}:*:table/{self.table_name}",
                        f"arn:aws:dynamodb:{self.region}:*:table/{self.table_name}/index/*"
                    ]
                }
            ]
        }
        
        role_name = f"{self.app_name}-amplify-role"
        
        try:
            # Create trust policy file
            with open("trust-policy.json", "w") as f:
                json.dump(trust_policy, f, indent=2)
            
            # Create permissions policy file
            with open("permissions-policy.json", "w") as f:
                json.dump(permissions_policy, f, indent=2)
            
            # Create IAM role
            subprocess.run([
                "aws", "iam", "create-role",
                "--role-name", role_name,
                "--assume-role-policy-document", "file://trust-policy.json"
            ], check=True)
            
            # Attach permissions policy
            subprocess.run([
                "aws", "iam", "put-role-policy",
                "--role-name", role_name,
                "--policy-name", f"{self.app_name}-dynamodb-policy",
                "--policy-document", "file://permissions-policy.json"
            ], check=True)
            
            # Clean up temp files
            os.remove("trust-policy.json")
            os.remove("permissions-policy.json")
            
            print(f"✅ Created IAM role '{role_name}'")
            return role_name
            
        except subprocess.CalledProcessError:
            print(f"⚠️ IAM role '{role_name}' may already exist")
            return role_name
    
    def create_amplify_app(self):
        """Create Amplify app and connect to GitHub."""
        print("🚀 Creating Amplify app...")
        
        # Get GitHub repository URL
        try:
            result = subprocess.run([
                "git", "config", "--get", "remote.origin.url"
            ], capture_output=True, text=True, check=True)
            
            repo_url = result.stdout.strip()
            if repo_url.startswith("https://github.com/"):
                repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
            else:
                print("❌ Repository must be hosted on GitHub")
                return None
            
        except subprocess.CalledProcessError:
            print("❌ Could not get GitHub repository URL")
            return None
        
        # Create Amplify app
        app_config = {
            "name": self.app_name,
            "description": "Amazon FC Employee Intelligence Platform with real-time sentiment analysis",
            "repository": repo_url,
            "platform": "WEB",
            "environmentVariables": {
                "AWS_REGION": self.region,
                "DYNAMODB_TABLE": self.table_name,
                "_LIVE_UPDATES": "[{\"name\":\"Amplify CLI\",\"pkg\":\"@aws-amplify/cli\",\"type\":\"npm\",\"version\":\"latest\"}]"
            },
            "buildSpec": """version: 1
applications:
  - frontend:
      phases:
        preBuild:
          commands:
            - pip install -r requirements.txt
            - python setup_aws_resources.py
        build:
          commands:
            - echo "Building Amazon FC Intelligence Platform"
            - python collect_initial_data.py
        postBuild:
          commands:
            - echo "Build completed successfully"
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
      cache:
        paths:
          - '.cache/**/*'"""
        }
        
        try:
            with open("app_config.json", "w") as f:
                json.dump(app_config, f, indent=2)
            
            result = subprocess.run([
                "aws", "amplify", "create-app",
                "--cli-input-json", "file://app_config.json"
            ], capture_output=True, text=True, check=True)
            
            app_info = json.loads(result.stdout)
            app_id = app_info["app"]["appId"]
            
            os.remove("app_config.json")
            
            print(f"✅ Created Amplify app with ID: {app_id}")
            return app_id
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create Amplify app: {e}")
            return None
    
    def create_branch_and_deploy(self, app_id):
        """Create branch and start deployment."""
        print("🌿 Creating branch and starting deployment...")
        
        branch_config = {
            "branchName": "main",
            "description": "Main production branch",
            "enableAutoBuild": True,
            "environmentVariables": {
                "AWS_REGION": self.region,
                "DYNAMODB_TABLE": self.table_name
            }
        }
        
        try:
            with open("branch_config.json", "w") as f:
                json.dump(branch_config, f, indent=2)
            
            result = subprocess.run([
                "aws", "amplify", "create-branch",
                "--app-id", app_id,
                "--cli-input-json", "file://branch_config.json"
            ], capture_output=True, text=True, check=True)
            
            os.remove("branch_config.json")
            
            # Start deployment
            result = subprocess.run([
                "aws", "amplify", "start-job",
                "--app-id", app_id,
                "--branch-name", "main",
                "--job-type", "RELEASE"
            ], capture_output=True, text=True, check=True)
            
            job_info = json.loads(result.stdout)
            job_id = job_info["jobSummary"]["jobId"]
            
            print(f"✅ Started deployment job: {job_id}")
            return job_id
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch or start deployment: {e}")
            return None
    
    def wait_for_deployment(self, app_id, job_id):
        """Wait for deployment to complete."""
        print("⏳ Waiting for deployment to complete...")
        
        max_wait_time = 1800  # 30 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                result = subprocess.run([
                    "aws", "amplify", "get-job",
                    "--app-id", app_id,
                    "--branch-name", "main",
                    "--job-id", job_id
                ], capture_output=True, text=True, check=True)
                
                job_info = json.loads(result.stdout)
                status = job_info["job"]["summary"]["status"]
                
                if status == "SUCCEED":
                    print("✅ Deployment completed successfully!")
                    return True
                elif status == "FAILED":
                    print("❌ Deployment failed!")
                    return False
                else:
                    print(f"🔄 Deployment status: {status}")
                    time.sleep(30)
                    
            except subprocess.CalledProcessError:
                print("⚠️ Could not check deployment status")
                time.sleep(30)
        
        print("⏰ Deployment timeout reached")
        return False
    
    def get_app_url(self, app_id):
        """Get the live app URL."""
        try:
            result = subprocess.run([
                "aws", "amplify", "get-app",
                "--app-id", app_id
            ], capture_output=True, text=True, check=True)
            
            app_info = json.loads(result.stdout)
            default_domain = app_info["app"]["defaultDomain"]
            
            app_url = f"https://main.{default_domain}"
            return app_url
            
        except subprocess.CalledProcessError:
            return None
    
    def populate_initial_data(self):
        """Populate DynamoDB with initial data."""
        print("📊 Populating initial data...")
        
        try:
            subprocess.run(["python", "collect_initial_data.py"], check=True)
            print("✅ Initial data populated successfully")
            return True
        except subprocess.CalledProcessError:
            print("⚠️ Could not populate initial data (will be done during build)")
            return False
    
    def deploy(self):
        """Run complete deployment process."""
        print("🚀 Starting AWS Amplify Deployment")
        print("=" * 50)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Create DynamoDB table
        if not self.create_dynamodb_table():
            return False
        
        # Step 3: Create IAM role
        role_name = self.create_iam_role()
        if not role_name:
            return False
        
        # Step 4: Populate initial data
        self.populate_initial_data()
        
        # Step 5: Commit and push changes
        print("📤 Committing and pushing changes...")
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m", 
                f"AWS Amplify deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("✅ Changes pushed to GitHub")
        except subprocess.CalledProcessError:
            print("⚠️ Could not push changes (may already be up to date)")
        
        # Step 6: Create Amplify app
        app_id = self.create_amplify_app()
        if not app_id:
            return False
        
        # Step 7: Create branch and deploy
        job_id = self.create_branch_and_deploy(app_id)
        if not job_id:
            return False
        
        # Step 8: Wait for deployment
        if not self.wait_for_deployment(app_id, job_id):
            return False
        
        # Step 9: Get app URL
        app_url = self.get_app_url(app_id)
        
        # Success!
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 50)
        print(f"📱 App ID: {app_id}")
        print(f"🌐 Live URL: {app_url}")
        print(f"🗄️ DynamoDB Table: {self.table_name}")
        print(f"🔐 IAM Role: {role_name}")
        print("\n✅ Your Amazon FC Intelligence Platform is now live on AWS!")
        
        return True

if __name__ == "__main__":
    deployer = AWSAmplifyDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Visit your live app URL")
        print("2. Verify data loads from DynamoDB")
        print("3. Set up monitoring and alerts")
        print("4. Configure automated data collection")
    else:
        print("\n❌ Deployment failed. Check the errors above.")
        exit(1)