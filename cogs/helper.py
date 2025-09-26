import requests
import html

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