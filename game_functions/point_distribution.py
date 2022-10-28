def point_distribution(table, data, total_answer):
    response_data=[]
    for item in data:
        points=0
        if "guess" in item and item["guess"] == total_answer:
            points=100
        elif "guess" in item and (item["guess"] == total_answer+1 or item["guess"] == total_answer-1):
            points=50
        table.update_item(
            Key={'connection_id': item["connection_id"]},
            UpdateExpression = "ADD points :p",
            ExpressionAttributeValues={
                ':p': points
        })
        item["last_turn_points"] = item["points"]
        item["points"]+= points
        response_data.append(item)

    return response_data