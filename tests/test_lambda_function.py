import sys
from pathlib import Path
path = str(Path(Path(__file__).parent.absolute()).parent.absolute())
sys.path.insert(0, path)

from lambda_function import lambda_handler
from dotenv import load_dotenv
load_dotenv()

event = {
    "requestContext": {
        "routeKey": "$connect",
        "connectionId": "test_id",
        "domainName": "2mgs44ly30.execute-api.us-east-1.amazonaws.com",
        "stage": "production"
    },
    "queryStringParameters": {
            "name":"user_name",
            "host":0,
            "room":"aaaa"
    }
}

print(lambda_handler(event, ""))