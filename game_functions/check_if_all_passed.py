def check_if_all_passed(table, room_id):
    scan_response = table.scan(
        FilterExpression="room_id = :id",
        ExpressionAttributeValues={
            ":id": room_id   
        })
    have_passed = [item["turn_status"] for item in scan_response['Items']]
    if "playing" in have_passed or "done" not in have_passed:
        return False
    else:
        return True
