# 🚀 AWS Amplify Deployment Guide - Real Data Platform

## ✅ COMPLETE AWS DEPLOYMENT SETUP

This guide will deploy your Amazon FC Intelligence Platform to AWS Amplify with real data persistence using DynamoDB.

---

## 🎯 STEP 1: AWS AMPLIFY SETUP

### **1.1 Create AWS Amplify App**
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Choose **GitHub** as source
4. Select repository: `lunchwolfjoe/amazon-fc-intelligence`
5. Branch: `main`

### **1.2 Build Settings**
Use the generated `amplify.yml` file:
```yaml
version: 1
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
            - echo "Build completed"
      artifacts:
        baseDirectory: /
        files:
          - '**/*'
```

### **1.3 Environment Variables**
Configure these in Amplify Console → App Settings → Environment Variables:

```
AWS_REGION = us-east-1
AWS_ACCESS_KEY_ID = [Your AWS Access Key]
AWS_SECRET_ACCESS_KEY = [Your AWS Secret Key]
REDDIT_CLIENT_ID = [Your Reddit Client ID]
REDDIT_CLIENT_SECRET = [Your Reddit Client Secret]
```

---

## 🗄️ STEP 2: AWS DYNAMODB SETUP

### **2.1 Create DynamoDB Table**
```bash
aws dynamodb create-table \
    --table-name amazon-fc-posts \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=created_utc,AttributeType=N \
    --key-schema \
        AttributeName=id,KeyType=HASH \
        AttributeName=created_utc,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### **2.2 Create Global Secondary Index**
```bash
aws dynamodb update-table \
    --table-name amazon-fc-posts \
    --attribute-definitions \
        AttributeName=subject_area,AttributeType=S \
        AttributeName=created_utc,AttributeType=N \
    --global-secondary-index-updates \
        '[{
            "Create": {
                "IndexName": "subject-area-index",
                "KeySchema": [
                    {"AttributeName": "subject_area", "KeyType": "HASH"},
                    {"AttributeName": "created_utc", "KeyType": "RANGE"}
                ],
                "Projection": {"ProjectionType": "ALL"},
                "BillingMode": "PAY_PER_REQUEST"
            }
        }]'
```

---

## 🔐 STEP 3: IAM PERMISSIONS

### **3.1 Create IAM Role for Amplify**
```json
{
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
                "arn:aws:dynamodb:us-east-1:*:table/amazon-fc-posts",
                "arn:aws:dynamodb:us-east-1:*:table/amazon-fc-posts/index/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "comprehend:DetectSentiment",
                "comprehend:DetectKeyPhrases"
            ],
            "Resource": "*"
        }
    ]
}
```

### **3.2 Attach Role to Amplify Service**
1. Go to IAM Console
2. Create role with above policy
3. Attach to Amplify service role

---

## ⚡ STEP 4: LAMBDA FUNCTION (OPTIONAL)

### **4.1 Create Data Collection Lambda**
```python
import json
import boto3
import praw
from datetime import datetime
import os

def lambda_handler(event, context):
    # Initialize services
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('amazon-fc-posts')
    
    # Reddit client
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        user_agent='AmazonFCIntelligence/1.0'
    )
    
    # Collect and store posts
    subreddit = reddit.subreddit('AmazonFC')
    posts_collected = 0
    
    for post in subreddit.hot(limit=50):
        table.put_item(
            Item={
                'id': post.id,
                'title': post.title,
                'content': post.selftext,
                'author': str(post.author),
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': int(post.created_utc),
                'collected_at': int(datetime.now().timestamp()),
                'subreddit': 'AmazonFC'
            }
        )
        posts_collected += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Collected {posts_collected} posts')
    }
```

### **4.2 Schedule Lambda with EventBridge**
```bash
aws events put-rule \
    --name "amazon-fc-data-collection" \
    --schedule-expression "rate(1 hour)" \
    --description "Hourly data collection for Amazon FC Intelligence"

aws lambda add-permission \
    --function-name amazon-fc-data-collector \
    --statement-id allow-eventbridge \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com
```

---

## 🚀 STEP 5: DEPLOY TO AMPLIFY

### **5.1 Commit and Push Changes**
```bash
git add .
git commit -m "AWS Amplify deployment with DynamoDB integration"
git push origin main
```

### **5.2 Trigger Amplify Build**
1. Go to Amplify Console
2. Your app will automatically build from the GitHub push
3. Monitor build logs for any issues
4. Build process will:
   - Install dependencies
   - Set up AWS resources
   - Populate initial data
   - Deploy Streamlit app

### **5.3 Access Your Live App**
- **URL**: `https://main.d[app-id].amplifyapp.com`
- **Features**: Real DynamoDB data, live updates, professional analytics

---

## 📊 STEP 6: VERIFY DEPLOYMENT

### **6.1 Check DynamoDB Data**
```bash
aws dynamodb scan \
    --table-name amazon-fc-posts \
    --select "COUNT" \
    --region us-east-1
```

### **6.2 Test Streamlit App**
1. Visit your Amplify URL
2. Verify data loads from DynamoDB
3. Test subject area filtering
4. Check post details and analytics

### **6.3 Monitor Performance**
- CloudWatch logs for Lambda function
- Amplify build logs
- DynamoDB metrics

---

## 🔧 STEP 7: ONGOING OPERATIONS

### **7.1 Data Updates**
- Lambda function runs hourly to collect new posts
- DynamoDB automatically scales with usage
- Streamlit app caches data for 30 minutes

### **7.2 Cost Optimization**
- DynamoDB: Pay-per-request pricing
- Lambda: Free tier covers most usage
- Amplify: Free tier for hosting

### **7.3 Monitoring & Alerts**
```bash
# Set up CloudWatch alarms
aws cloudwatch put-metric-alarm \
    --alarm-name "DynamoDB-HighReadCapacity" \
    --alarm-description "Monitor DynamoDB read capacity" \
    --metric-name ConsumedReadCapacityUnits \
    --namespace AWS/DynamoDB \
    --statistic Sum \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold
```

---

## ✅ SUCCESS CHECKLIST

### **Infrastructure**
- [ ] AWS Amplify app created and configured
- [ ] DynamoDB table created with proper schema
- [ ] IAM roles and permissions configured
- [ ] Environment variables set in Amplify

### **Application**
- [ ] Streamlit app connects to DynamoDB
- [ ] Data loads and displays correctly
- [ ] Subject area classification works
- [ ] Analytics charts render properly

### **Data Pipeline**
- [ ] Initial data populated in DynamoDB
- [ ] Lambda function deployed (optional)
- [ ] Automated data collection scheduled
- [ ] Data freshness monitoring active

### **Monitoring**
- [ ] CloudWatch logs configured
- [ ] Performance metrics tracked
- [ ] Cost monitoring enabled
- [ ] Error alerting set up

---

## 🎯 FINAL RESULT

**Your Amazon FC Intelligence Platform will be:**

✅ **Live on AWS Amplify** with professional hosting
✅ **Real Data Persistence** using DynamoDB
✅ **Automated Updates** via Lambda functions
✅ **Scalable Architecture** that grows with usage
✅ **Cost Optimized** with AWS free tier benefits
✅ **Enterprise Ready** with monitoring and alerts

**Live URL**: `https://main.d[your-app-id].amplifyapp.com`

---

## 🆘 TROUBLESHOOTING

### **Common Issues**

**Build Fails:**
- Check environment variables are set
- Verify AWS credentials have proper permissions
- Review Amplify build logs

**No Data Loading:**
- Verify DynamoDB table exists
- Check IAM permissions for DynamoDB access
- Run `collect_initial_data.py` manually

**Performance Issues:**
- Enable DynamoDB caching
- Optimize Streamlit queries
- Monitor CloudWatch metrics

**Cost Concerns:**
- Review DynamoDB usage patterns
- Optimize Lambda execution frequency
- Monitor AWS billing dashboard

---

## 🎉 DEPLOYMENT COMPLETE!

**Your Amazon FC Intelligence Platform is now running on enterprise-grade AWS infrastructure with real data persistence and automated updates!**