import requests

# replace with your client ID
client_id = "TlpFlAS12F2xucj2B4Q" 

# replace with your account ID
account_id = "pESewot8S8qetqaVY85eZA" 

# replace with your client secret
client_secret = "4Ftc4Hczl5jfk6IlWYgJrCqP4wd1Uu6P" 

auth_token_url = "https://zoom.us/oauth/token"
api_base_url = "https://api.zoom.us/v2"

# create the Zoom link function
def create_meeting(topic, start_date, start_time):
        data = {
        "grant_type": "account_credentials",
        "account_id": account_id,
        "client_secret": client_secret
        }
        response = requests.post(auth_token_url, 
                                 auth=(client_id, client_secret), 
                                 data=data)
        
        if response.status_code!=200:
            print("Unable to get access token")
        response_data = response.json()
        access_token = response_data["access_token"]

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "topic": topic,
             "authentication_exception": [
            {
                "email": "chungdaeun154@gmail.com",
            }
            ],
            'start_time': f'{start_date}T10:{start_time}',
            "type": 2
        }

        resp = requests.post(f"{api_base_url}/users/me/meetings", 
                             headers=headers, 
                             json=payload)
        
        if resp.status_code!=201:
            print("Unable to generate meeting link")
        response_data = resp.json()
        
        content = {
                    "meeting_url": response_data["join_url"], 
                    "password": response_data["password"],
                    "meetingTime": response_data["start_time"],
                    "purpose": response_data["topic"],
                    "message": "Success",
                    "status":1
        }
        print(content)

create_meeting(
      "Test Zoom Meeting",
      "2023-10-23",
      "18:24",
      )