import boto3, os
from moto import mock_dynamodb

@mock_dynamodb
def mock_table():
    my_session = boto3.session.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
        region_name = "us-east-1",
    )
    ddb = my_session.resource('dynamodb', region_name = "us-east-1")
    table_name = "test"
    ddb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'connection_id','KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'connection_id','AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
        )
    table = ddb.Table(table_name)
    return table
