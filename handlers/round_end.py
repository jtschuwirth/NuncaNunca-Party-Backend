import json

from decimal import Decimal
from game_functions.getNewPrompt import getNewPrompt

from auxiliary_functions.get_all_recipients import get_all_recipients
from auxiliary_functions.handle_ws_message import handle_ws_message


def round_end(table, room_id, apig_management_client):

    status_code = 200
    data=[]
    total_answer=0
    try:
        scan_response = table.scan(
            FilterExpression="room_id = :id",
            ExpressionAttributeValues={
                ":id": room_id   
        })
        for item in scan_response['Items']:
            if item["turn_status"] == "hosting":
                level = item["lvl"]
                index = item[f"current_lvl{level}"]
                table.update_item(
                        Key={'connection_id': item["connection_id"]},
                        UpdateExpression = f"ADD current_lvl{level} :v",
                        ExpressionAttributeValues={
                            ':v': 1
                })
                continue

            Item={}
            for key, attribute in item.items():
                if isinstance(attribute, Decimal):
                    Item[key] = int(attribute)
                    if key == "answer":
                        total_answer+=Item[key]
                else:
                    Item[key] = attribute
            data.append(Item)

            table.update_item(
                Key={'connection_id': item["connection_id"]},
                UpdateExpression = "SET turn_status = :status",
                ExpressionAttributeValues={
                    ':status': "playing"
            })
    except:
        return 404

    response_data=[]
    try:
        for item in data:
            points=0
            if item["guess"] == total_answer:
                points=100
            elif item["guess"] == total_answer+1 or item["guess"] == total_answer-1:
                points=50
            table.update_item(
                Key={'connection_id': item["connection_id"]},
                UpdateExpression = "ADD points :p",
                ExpressionAttributeValues={
                    ':p': points
            })

            if not "points" in item:
                item["last_turn_points"] = 0
                item["points"] = points
            else:
                item["last_turn_points"] = item["points"]
                item["points"]+= points

            response_data.append(item)
    except:
        status_code=503
    
    maximum_recon_tries = 3
    reconnection_tries = 0

    while reconnection_tries < maximum_recon_tries:
        try:
            prompt = getNewPrompt(level, index, room_id)
            if prompt["phrase"]:
                break
            else:
                prompt = 0
        except:
            prompt = 0

        reconnection_tries+=1

    if not prompt:
        prompt = {"phrase": "Error fetching prompt", "lvl":1}

    try:
        recipients = get_all_recipients(table, room_id)
        message = json.dumps({"round_end": response_data, "new_prompt": prompt})
        handle_ws_message(table, recipients, message, apig_management_client)
    except:
        status_code = 503

    return status_code