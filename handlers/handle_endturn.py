import json

from handlers.turn_end import turn_end
from handlers.round_end import round_end
from game_functions.check_if_all_passed import check_if_all_passed

def handle_endturn(table, event, connection_id, apig_management_client):
    body = event.get('body')
    body = json.loads(body)

    table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression = "SET turn_status = :status",
            ExpressionAttributeValues={
                ':status': "done"
    })

    table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression = "SET answer = :answer",
            ExpressionAttributeValues={
                ':answer': body["answer"]
    }) 

    table.update_item(
            Key={'connection_id': connection_id},
            UpdateExpression = "SET guess = :guess",
            ExpressionAttributeValues={
                ':guess': body["guess"]
    }) 

    item_response = table.get_item(Key={'connection_id': connection_id})
    room_id = item_response['Item']['room_id']

    if check_if_all_passed(table, room_id):
        return round_end(table, room_id, apig_management_client)
    else:
        return turn_end(table, connection_id, item_response, apig_management_client)