import requests

def getNewPrompt(level, index, room_id):
    maximum_recon_tries = 3
    reconnection_tries = 0

    while reconnection_tries < maximum_recon_tries:
        try:
            if not level: level = 1
            response = requests.get(url=f"https://59fxcxkow4.execute-api.us-east-1.amazonaws.com/dev/nuncanunca/phrases/room?level={level}&index={index}&room_id={room_id}")
            if response.status_code == 200:
                prompt = response.json()[0]
            else:
                prompt = 0

            if prompt["phrase"]:
                break
            else:
                prompt = 0
        except:
            prompt = 0

        reconnection_tries+=1

    if not prompt:
        prompt = {"phrase": "Error fetching prompt", "lvl":1}
    
    return prompt
