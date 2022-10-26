import requests

def getNewPrompt(level, index, room_id):
    if not level: level = 1
    response = requests.get(url=f"https://59fxcxkow4.execute-api.us-east-1.amazonaws.com/dev/nuncanunca/phrases/room?level={level}&index={index}&room_id={room_id}")
    if response.status_code == 200:
        return response.json()[0]
    else:
        return 0