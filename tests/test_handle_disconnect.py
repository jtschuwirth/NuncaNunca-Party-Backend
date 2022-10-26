import sys, os
import boto3
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from handlers.handle_disconnect import handle_disconnect


my_session = boto3.session.Session(
        aws_access_key_id=os.environ.get("ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("SECRET_KEY"),
        region_name = "us-east-1",
    )
table_name = os.environ['TABLE_NAME']
table = my_session.resource('dynamodb').Table(table_name)

dummy_event = {
    "requestContext": {
        'routeKey': "route",
        'domainName': "domain",   
    },
    'queryStringParameters': {
        "name":"user_name",
        "host":0,
        "room":"aaaa"
    }
}

connection_id = "test_id"
apig_management_client = "client"

handle_disconnect(table, dummy_event, connection_id, apig_management_client)