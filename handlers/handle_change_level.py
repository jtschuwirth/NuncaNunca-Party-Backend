import json
from botocore.exceptions import ClientError

def handle_change_level(table, event, connection_id, apig_management_client):
    status_code = 200
    body = event.get('body')
    body = json.loads(body)
    level = body["level"]

    try:
        table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression = "SET lvl = :lvl",
            ExpressionAttributeValues={
                ':lvl': level
        })
        
    except ClientError:
        status_code=503
    

    return status_code