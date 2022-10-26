import json

from botocore.exceptions import ClientError
from auxiliary_functions.handle_ws_message import handle_ws_message
from auxiliary_functions.get_all_recipients import get_all_recipients

def handle_connect(table, event, connection_id, apig_management_client):
    user_name = event.get('queryStringParameters', {'name': 'guest'}).get('name')
    is_host = event.get('queryStringParameters', {'host': 0}).get("host")
    room_id = event.get('queryStringParameters', {'room': "aaaa"}).get("room")

    status_code = 200
    try:
        if is_host:
            table.put_item(Item={
                'connection_id': connection_id,
                'room_id': room_id,
                'user_name': user_name,
                "turn_status": "hosting",
                "lvl":1,
                "current_lvl1":1,
                "current_lvl2":0,
                "current_lvl3":0
            })
        else:
            table.put_item(Item={
                'connection_id': connection_id, 
                'room_id': room_id, 
                'user_name': user_name, 
                "turn_status": "waiting",
                "points":0
            })
        recipients = get_all_recipients(table, room_id)
        message = json.dumps({"new_connection":{"id": connection_id, "user_name": user_name, "points":0}})
        handle_ws_message(table, recipients, message, apig_management_client)
    except ClientError:
        status_code = 503
    return status_code