import json
def get_id_from_element(array_element):
    result=""
    result=array_element.replace("\"", "")
    index=result.index("block_id:")
    result=result[index+9:]
    result.replace(" ", "")
    return result

x={'type': 'block_actions', 'user': {'id': 'U05H8AK3T7W', 'username': 'dae', 'name': 'dae', 'team_id': 'T05H5PH3U4B'}, 'api_app_id': 'A05KCSEG63W', 'token': 'I6lwcLzFnloi1CRyU5epmGPz', 'container': {'type': 'message_attachment', 'message_ts': '1698002200.326609', 'attachment_id': 1, 'channel_id': 'C05H2V0ANSZ', 'is_ephemeral': False, 'is_app_unfurl': False, 'thread_ts': '1698002199.463959'}, 'trigger_id': '6100029227744.5583799130147.252d0eb831b6c3820d493217b9e4e52a', 'team': {'id': 'T05H5PH3U4B', 'domain': 'dogfoodtestin-an22161'}, 'enterprise': None, 'is_enterprise_install': False, 'channel': {'id': 'C05H2V0ANSZ', 'name': 'general'}, 'message': {'bot_id': 'B05KABL9T3M', 'type': 'message', 'text': '', 'user': 'U05K7GSDQ69', 'ts': '1698002200.326609', 'app_id': 'A05KCSEG63W', 'team': 'T05H5PH3U4B', 'attachments': [{'id': 1, 'blocks': [{'type': 'section', 'block_id': 'rztJi', 'text': {'type': 'plain_text', 'text': "Hi, I'm here to schedule a Zoom meeting with EventCAT. Please pick a date and time for the meeting as well as the meeting host. Thank you so much.", 'emoji': True}}, {'type': 'divider', 'block_id': 'Sgo5N'}, {'type': 'input', 'block_id': 'NMvaK', 'label': {'type': 'plain_text', 'text': 'Pick a date & time for a Zoom meeting', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'datetimepicker', 'action_id': 'datetime_input', 'initial_date_time': 1628633820}}, {'type': 'divider', 'block_id': 'ULOVf'}, {'type': 'input', 'block_id': 'azvjH', 'label': {'type': 'plain_text', 'text': 'Select the meeting host', 'emoji': True}, 'optional': False, 'dispatch_action': False, 'element': {'type': 'multi_users_select', 'action_id': 'meetinghost_input', 'placeholder': {'type': 'plain_text', 'text': 'Select users', 'emoji': True}}}, {'type': 'divider', 'block_id': '1/1sr'}, {'type': 'actions', 'block_id': 'T7Q8W', 'elements': [{'type': 'button', 'action_id': 'actionId-0', 'text': {'type': 'plain_text', 'text': 'Complete', 'emoji': True}, 'value': 'click_me_123'}]}], 'fallback': '[no preview available]'}], 'thread_ts': '1698002199.463959', 'parent_user_id': 'U05H8AK3T7W'}, 'state': {'values': {'NMvaK': {'datetime_input': {'type': 'datetimepicker', 'selected_date_time': 1628633820}}, 'azvjH': {'meetinghost_input': {'type': 'multi_users_select', 'selected_users': ['U05H8AK3T7W']}}}}, 'response_url': 'https://hooks.slack.com/actions/T05H5PH3U4B/6074113791269/pyhGdenNXQLd58t4foB81hyl', 'actions': [{'action_id': 'actionId-0', 'block_id': 'T7Q8W', 'text': {'type': 'plain_text', 'text': 'Complete', 'emoji': True}, 'value': 'click_me_123', 'type': 'button', 'action_ts': '1698002205.045734'}]}
x1=json.dumps(x)
y = json.loads(x1)

# the result is a Python dictionary:
block=y["message"]["attachments"]

x2=json.dumps(block)
x2.replace(",", "")
list=x2.rsplit("{")
list2=[]

for x in list:
    if "block_id" in x:
        list2.append(x)

BLOCK_ID_TIME_DATE=""
BLOCK_ID_USER=""
n=0
for x in list:
    if "\"type\": \"input\"" in x:
        if n==0:
            BLOCK_ID_TIME_DATE=x
            n=n+1
        elif n==1:
            BLOCK_ID_USER=x

list3=BLOCK_ID_TIME_DATE.split(",")
list4=BLOCK_ID_USER.split(",")

BLOCK_ID_TIME_DATE=list3[1]
BLOCK_ID_USER=list4[1]

BLOCK_ID_TIME_DATE=get_id_from_element(BLOCK_ID_TIME_DATE)
BLOCK_ID_USER=get_id_from_element(BLOCK_ID_USER)

selected_date=y["state"]["values"][BLOCK_ID_TIME_DATE]["datetime_input"]["selected_date_time"]

print(selected_date)