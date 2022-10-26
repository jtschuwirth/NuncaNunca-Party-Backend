import json

from botocore.exceptions import ClientError
from auxiliary_functions.get_all_recipients import get_all_recipients
from auxiliary_functions.handle_ws_message import handle_ws_message

def turn_end(table, connection_id, item_response, apig_management_client):
    status_code = 200

    try:
        user_name = item_response['Item']['user_name']
        points = int(item_response['Item']['points'])
        room_id = item_response['Item']['room_id']
        recipients = get_all_recipients(table, room_id)
        message = json.dumps({"turn_end":{"id": connection_id, "user_name": user_name, "points":points}})
        handle_ws_message(table, recipients, message, apig_management_client)
    except ClientError:
        status_code=503

    return status_code