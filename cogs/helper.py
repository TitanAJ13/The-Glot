import requests
from requests.auth import AuthBase
import html
import os

def handleResponse(response: requests.Response, success: str) -> str:
    try:
        response.raise_for_status()
        json = response.json()
        if (json['status'] == 'success'):
            return success
        else:
            return "Something went wrong..."
    except requests.HTTPError as e:
        return "ERROR: " + parseError(e)
    except Exception as e:
        return f"ERROR: {e}"
    
def parseError(error: requests.HTTPError) -> str:
    description = error.response.text.split("<p>")[1].split("</p>")[0]
    return html.unescape(description)

class BearerAuth(AuthBase):
    def __init__(self):
        super().__init__()

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {os.getenv('BEARER')}"
        return r