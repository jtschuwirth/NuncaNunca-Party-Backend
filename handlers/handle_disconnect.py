import json

from botocore.exceptions import ClientError

from auxiliary_functions.handle_ws_message import handle_ws_message
from auxiliary_functions.get_all_recipients import get_all_recipients
from game_functions.check_if_all_passed import check_if_all_passed
from handlers.round_end import round_end


def handle_disconnect(table, event, connection_id, apig_management_client):
    status_code = 200
    try:
        item_response = table.get_item(Key={'connection_id': connection_id})
        table.delete_item(Key={'connection_id': connection_id})
        room_id = item_response['Item']['room_id']
        recipients = get_all_recipients(table, room_id)
        message = json.dumps({"disconnected": connection_id})
        handle_ws_message(table, recipients, message, apig_management_client)
        
        if check_if_all_passed(table, room_id):
            return round_end(table, room_id, apig_management_client)
        
    except ClientError:
        status_code = 503
    return status_code
