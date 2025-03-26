import json
import requests

from config.config import LOCAL_URL


class Notification:
    def __init__(self) -> None:
        self.url = f"http://{LOCAL_URL}:8000/notify"

    def send_notification(self, title, message):
        payload = json.dumps({"title": title, "message": message})
        headers = {"Content-Type": "application/json"}

        response = requests.request("POST", self.url, headers=headers, data=payload)

        userResponse = json.loads(response.text)["clicked"]
        return userResponse
