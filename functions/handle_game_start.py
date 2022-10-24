import json
from botocore.exceptions import ClientError

from functions.get_all_recipients import get_all_recipients
from functions.handle_ws_message import handle_ws_message
from functions.getNewPrompt import getNewPrompt

def handle_game_start(table, connection_id, apig_management_client):
    status_code = 200

    try:
        item_response = table.get_item(Key={'connection_id': connection_id})
        if item_response["Item"]["turn_status"] != "hosting":
            return 403

        room_id = item_response['Item']['room_id']

        recipients = get_all_recipients(table, room_id)
        for con_id in recipients:
            if con_id != connection_id:
                table.update_item(
                    Key={'connection_id': con_id},
                    UpdateExpression = "SET turn_status = :status",
                    ExpressionAttributeValues={
                        ':status': "playing"
                }) 

        prompt = getNewPrompt(item_response["Item"]["lvl"])
        message = json.dumps({"starting_game": prompt})
        handle_ws_message(table, recipients, message, apig_management_client)
        
    except ClientError:
        status_code=503
    

    return status_code