
import boto3
import os

def setup_aws_resources():
    try:
        # Create DynamoDB table if it doesn't exist
        dynamodb = boto3.resource('dynamodb')
        
        table_name = 'amazon-fc-posts'
        existing_tables = [table.name for table in dynamodb.tables.all()]
        
        if table_name not in existing_tables:
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_utc', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'created_utc', 'AttributeType': 'N'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            print(f"Created DynamoDB table: {table_name}")
        else:
            print(f"DynamoDB table {table_name} already exists")
            
    except Exception as e:
        print(f"Error setting up AWS resources: {e}")

if __name__ == "__main__":
    setup_aws_resources()
