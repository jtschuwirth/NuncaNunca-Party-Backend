import json

from botocore.exceptions import ClientError
from auxiliary_functions.handle_ws_message import handle_ws_message
from auxiliary_functions.get_all_recipients import get_all_recipients

def handle_connect(table, event, connection_id, apig_management_client):
    status_code = 200
    
    user_name = event.get('queryStringParameters', {'name': 'guest'}).get('name')
    is_host = event.get('queryStringParameters', {'host': 0}).get("host")
    room_id = event.get('queryStringParameters', {'room': "aaaa"}).get("room")

    is_there_host=0
    players = {}

    scan_response = table.scan(
        FilterExpression="room_id = :id",
        ExpressionAttributeValues={
                ":id": room_id   
        })
    for item in scan_response["Items"]:
        if item["turn_status"] == "hosting":
            is_there_host = 1
        else:
            players[item["user_name"]] = {"connection_id": item["connection_id"], 
                                          "points": item["points"], 
                                          "turn_status": item["turn_status"]}

    try:
        message = json.dumps({"new_connection":{"id": connection_id, "user_name": user_name, "points":0}})
        if is_host and not is_there_host:
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

        elif not is_host and is_there_host and user_name not in players:
            table.put_item(Item={
                'connection_id': connection_id, 
                'room_id': room_id, 
                'user_name': user_name, 
                "turn_status": "waiting",
                "points":0
            })
        
        elif not is_host and is_there_host and user_name in players and players[user_name]["turn_status"] == "disconnected" and players[user_name]["connection_id"] != connection_id:
            table.put_item(Item={
                'connection_id': connection_id, 
                'room_id': room_id, 
                'user_name': user_name, 
                "turn_status": "waiting",
                "points": players[user_name]["points"]
            })
            table.delete_item(Key={'connection_id': players[user_name]["connection_id"]})
        else:
            message = json.dumps({"connection_error": "error connecting to this room"})
            status_code = 503

        recipients = get_all_recipients(table, room_id)
        handle_ws_message(table, recipients, message, apig_management_client)
    except ClientError:
        status_code = 503
    return status_code