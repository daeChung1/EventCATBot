import json
import logging
import string
logging.basicConfig(level=logging.DEBUG)
import time
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import app 
from pathlib import Path 
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
from slackeventsapi import SlackEventAdapter
import requests
from flask_mail import Mail, Message
from datetime import datetime

env_path=Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter=SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], '/slack/events', app)
mail=Mail(app)

#FOR SLACK APP  
client=WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID=client.api_call("auth.test")['user_id']
DETECT_MESSAGES=['meeting', 'zoom', 'eventcat', 'schedule']
BLOCK_ID_TIME_DATE=""
BLOCK_ID_USER=""

# STORE_ALL_MESSAGE()

#FOR ZOOM APP
client_id = os.environ['ZOOM_CLIENT_ID']
account_id = os.environ['ZOOM_ACCOUNT_ID']
client_secret = os.environ['ZOOM_CLIENT_SECRET']
auth_token_url = "https://zoom.us/oauth/token"
api_base_url = "https://api.zoom.us/v2"
meeting_url=""
meeting_time=""
meeting_password=""
meeting_topic=""

#FOR MAILING
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'slacktestingeventcat'
app.config['MAIL_PASSWORD'] = 'a1234567!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# app.config['MAIL_SERVER']='smtp.mandrillapp.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USERNAME'] = 'eventcat'
# app.config['MAIL_PASSWORD'] = 'md-RCyG70-NJNkqd27_DRwT0Q'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

current_time=int(time.time())

message_counts={}
meeting_scheduling_messages={}

class SchedulingMessage:
    SCHEDULING_MESSAGE={
	"blocks": [
		{
			"type": "section",
			"text": {
				"type": "plain_text",
				"text": "Hi, I'm here to schedule a Zoom meeting with EventCAT. Please pick a date and time for the meeting as well as the meeting host. Thank you so much.",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "datetimepicker",
				"action_id": "datetime_input",
				"initial_date_time": current_time
			},
			"label": {
				"type": "plain_text",
				"text": "Pick a date & time for a Zoom meeting"
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "input",
			"element": {
				"type": "multi_users_select",
				"placeholder": {
					"type": "plain_text",
					"text": "Select users",
					"emoji": True
				},
				"action_id": "meetinghost_input"
			},
			"label": {
				"type": "plain_text",
				"text": "Select the meeting participants",
				"emoji": True
			}
		},
		{
			"type": "divider"
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Complete",
						"emoji": True
					},
					"value": "click_me_123",
					"action_id": "actionId-0"
				}
			]
		}
	]
}
    def __init__(self, channel, user):
        self.channel=channel
        self.user=user
        self.icon_emoji=':robot_face:'
        self.timestamp=''
        self.meeting_completed=False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'username': 'EventCAT Robot!',
            'icon_emoji': self.icon_emoji,
            'blacks': [
                self.SCHEDULING_MESSAGE,
                self._get_reaction_meeting()
            ]
        }
    
    def _get_reaction_meeting(self):
        checkmark=':white_check_mark:'
        if not self.completed:
            checkmark=':white_large_squre:'
        
        text=f'{checkmark} *React to this message!*'

        return {'type': 'section', 'text': {'type': 'mrkdwm', 'text': text}}

def send_scheduling_message(channel, user):
    scheduling=SchedulingMessage(channel, user)
    message = scheduling.get_message()
    response=client.chat_postMessage(**message)
    scheduling.timestamp=response['ts']

    if channel not in meeting_scheduling_messages:
        meeting_scheduling_messages[channel]={}
    meeting_scheduling_messages[channel][user]=scheduling

def detect_messages(message):
    msg=message.lower()
    msg=msg.translate(str.maketrans('', '', string.punctuation))
    return any(word in msg for word in DETECT_MESSAGES)

def send_message(channel_id, ts):
        current_time=int(time.time())
        client.chat_postMessage(channel=channel_id, thread_ts=ts, text="", attachments=[])

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
            "start_time": f'{start_date}T10:{start_time}',
            "timezone": "America/Los_Angeles",
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
        return content

@app.route("/") 
def draft_send_email_to_participants(email_list, payload, date, time):
    zoom_url=payload.get('meeting_url')
    print(zoom_url)
    passowrd=payload.get('password')
    email_draft="Hello, \n I'd like to invite you to a Zoom meeting on "+date+" at "+time+". \n To join the Zoom meeting, please use this Zoom link:"+zoom_url
    msg = Message(subject='Zoom Meeting Invitation', sender='contact@eventcat.live', recipients=email_list)
    msg.body = email_draft
    mail.send(msg)

def get_id_from_element(array_element):
    result=""
    result=array_element.replace("\"", "")
    index=result.index("block_id:")
    result=result[index+10:]
    result.replace(" ", "")
    return result

def get_block_id_from_json(slack_req):
    y=slack_req

    # the result is a Python dictionary:
    block=y["message"]["attachments"]

    x2=json.dumps(block)
    x2.replace(",", "")
    list=x2.rsplit("{")
    list2=[]

    for x in list:
        if "block_id" in x:
            list2.append(x)

    n=0
    for x in list:
        if "\"type\": \"input\"" in x:
            if n==0:
                time_date_id=x
                n=n+1
            elif n==1:
                user_id=x

    list3=time_date_id.split(",")
    list4=user_id.split(",")

    time_date_id=list3[1]
    user_id=list4[1]

    time_date_id=get_id_from_element(time_date_id)
    user_id=get_id_from_element(user_id)

    result=[time_date_id, user_id]
    return result

def find_meeting_host_email_address(meeting_host):
    email=[]
    print(meeting_host[0])
    for x in meeting_host:
        payload=client.users_profile_get(user=x)
        user_email=payload['profile']['email']
        email.append(user_email)
    return email

@slack_event_adapter.on('message')
def message(payload):
    event=payload.get('event', {})
    channel_id=event.get('channel')
    user_id=event.get('user')
    text=event.get('text')

    if user_id != None and BOT_ID!=user_id:
        ts=event.get('ts')
        send_message(channel_id, ts)
        if user_id in message_counts:
            message_counts[user_id]+=1
        else:
            message_counts[user_id]=1
        if detect_messages(text):
            send_scheduling_message(channel_id, user_id)
#send_scheduling_message(f'@{user_id}', user_id) ==> will send a direct message to the user

@slack_event_adapter.on('reaction_added')
def reaction_to_send_the_transcript(payload):
    event=payload.get('event', {})
    channel_id=event.get('channel')
    user_id=event.get('user')

@app.route('/slack/actions', methods=['POST'])
def handle_slack_actions():
    slack_req = json.loads(request.form.get('payload'))
    response = '{"text": "Hi, <@' + slack_req["user"]["id"] + '>"}'
    id_array=get_block_id_from_json(slack_req)
    BLOCK_ID_TIME_DATE=id_array[0]
    BLOCK_ID_USER=id_array[1]
    meeting_date_time=slack_req['state']['values'][BLOCK_ID_TIME_DATE]['datetime_input']['selected_date_time']
    meeting_host=slack_req['state']['values'][BLOCK_ID_USER]['meetinghost_input']['selected_users']
    unix_meeting_date_time=int(meeting_date_time)
    date=(datetime.fromtimestamp(unix_meeting_date_time).strftime('%Y-%m-%d'))
    time=(datetime.fromtimestamp(unix_meeting_date_time).strftime('%H:%M'))
    participants_email=find_meeting_host_email_address(meeting_host)
    zoom_content=create_meeting("Zoom Meeting", date, time)
    draft_send_email_to_participants(participants_email, zoom_content, date, time)
    return response, 200, {'content-type': 'application/json'}  

@app.route('/schedule-eventcat', methods=['GET', 'POST'])
def schedule_eventcat():
    data=request.form
    user_id=data.get('user_id')
    channel_id=data.get('channel_id')
    ts=data.get('ts')
    send_message(channel_id, ts)
    return Response(), 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)


#Why I couldn't find the solutions from Google?
#python flask 403 forbidden ==> googling key words

# Zoom App: 
# meeting that EventCAT can join ==>
# final goal = creating a zoom meeting
# Button Click ==> Zoom meeting url https://us06web.zoom.us/meeting/schedule ==> should be opened
# meeting ==> have to invite someone/should make Zoom allow users to choose the meeting participants
# original plan: sending the meeting url
# have to use Zoom API ==> Zoom App (should be created in first place in order to use the APIs) 
# Zoom API tokens ==> Zoom App needed ==> should be able \


#recap: before clicking the button ==> choose the meeting date/time + participants ==> server receives the information
#list of emails of the participants + eventcat xl8.ai account bot@xl8.ai (bot email address) *should always be added to the partcipant list
#schedule the meeting using the zoom api ==> send the meeting reminder email to the users 

#two main functions
#/slack/events ==> call the bot
#/slack/actions ==> when the input is submitted, it receives the information. 

# {'type': 'block_actions', 'user': {'id': 'U05H8AK3T7W', 'username': 'dae', 'name': 'dae', 'team_id': 'T05H5PH3U4B'}, 'api_app_id': 'A05KCSEG63W', 'token': 'I6lwcLzFnloi1CRyU5epmGPz', 'container': {'type': 'message_attachment', 'message_ts': '1695346396.301629', 'attachment_id': 1, 'channel_id': 'C05H2V0ANSZ', 'is_ephemeral': False, 'is_app_unfurl': False, 'thread_ts': '1695346395.581579'}, 'trigger_id': '5933532806370.5583799130147.e68dd8341c628c773fb7040118ae72c5', 'team': {'id': 'T05H5PH3U4B', 'domain': 'dogfoodtestin-an22161'}, 'enterprise': None, 'is_enterprise_install': False, 'channel': {'id': 'C05H2V0ANSZ', 'name': 'general'}, 'message': {'bot_id': 'B05KABL9T3M', 'type': 'message', 'text': '', 'user': 'U05K7GSDQ69', 'ts': '1695346396.301629', 'app_id': 'A05KCSEG63W', 'team': 'T05H5PH3U4B', 'attachments': [{'id': 1, 'blocks': [{'type': 'section', 'block_id': '/oJae', 'text': {'type': 'plain_text', 'text': 'Hi, I am here to assist scheduling your Zoom meeting. Please select meeting date and time.', 'emoji': True}}, {'type': 'divider', 'block_id': 'zz43'}, {'type': 'input', 'block_id': 'yzsG', 'label': {'type': 'plain_text', 'text': 'Meeting Date and Time', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'datetimepicker', 'action_id': 'datetimeinput1', 'initial_date_time': 1628633820}}, {'type': 'divider', 'block_id': '40HF'}, {'type': 'actions', 'block_id': 'Ehwd', 'elements': [{'type': 'button', 'action_id': 'actionId-0', 'text': {'type': 'plain_text', 'text': 'Click Me', 'emoji': True}, 'value': 'click_me_123'}]}], 'fallback': '[no preview available]'}], 'thread_ts': '1695346395.581579', 'parent_user_id': 'U05H8AK3T7W'}, 'state': {'values': {'yzsG': {'datetimeinput1': {'type': 'datetimepicker', 'selected_date_time': 1628633820}}}}, 'response_url': 'https://hooks.slack.com/actions/T05H5PH3U4B/5956527243280/WEooiHF85WyAbFFTuwjKq27y', 'actions': [{'action_id': 'actionId-0', 'block_id': 'Ehwd', 'text': {'type': 'plain_text', 'text': 'Click Me', 'emoji': True}, 'value': 'click_me_123', 'type': 'button', 'action_ts': '1695346663.574505'}]}
#scheduling message type:
# {
# 	"blocks": [
# 		{
# 			"type": "section",
# 			"text": {
# 				"type": "plain_text",
# 				"text": "Hi, I'm here to schedule a Zoom meeting with EventCAT. Please pick a date and time for the meeting as well as the meeting host. Thank you so much.",
# 				"emoji": True
# 			}
# 		},
# 		{
# 			"type": "divider"
# 		},
# 		{
# 			"type": "input",
# 			"element": {
# 				"type": "datetimepicker",
# 				"action_id": "datetime_input",
# 				"initial_date_time": current_time
# 			},
# 			"label": {
# 				"type": "plain_text",
# 				"text": "Pick a date & time for a Zoom meeting"
# 			}
# 		},
# 		{
# 			"type": "divider"
# 		},
# 		{
# 			"type": "input",
# 			"element": {
# 				"type": "multi_users_select",
# 				"placeholder": {
# 					"type": "plain_text",
# 					"text": "Select users",
# 					"emoji": True
# 				},
# 				"action_id": "meetinghost_input"
# 			},
# 			"label": {
# 				"type": "plain_text",
# 				"text": "Select the meeting participants",
# 				"emoji": True
# 			}
# 		},
# 		{
# 			"type": "divider"
# 		},
# 		{
# 			"type": "actions",
# 			"elements": [
# 				{
# 					"type": "button",
# 					"text": {
# 						"type": "plain_text",
# 						"text": "Complete",
# 						"emoji": True
# 					},
# 					"value": "click_me_123",
# 					"action_id": "actionId-0"
# 				}
# 			]
# 		}
# 	]
# }