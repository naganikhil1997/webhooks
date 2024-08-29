from flask import Flask, request, make_response, jsonify
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '')
PAGE_ID = os.getenv('PAGE_ID', '')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN', '')

@app.route('/webhook/messaging-webhook', methods=['GET', 'POST'])
def messaging_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return make_response(challenge, 200)
            else:
                return make_response('Forbidden', 403)
        return make_response('Bad Request', 400)

    if request.method == 'POST':
        body = request.get_json()

        if not body or 'entry' not in body:
            return make_response('Bad Request', 400)

        try:
            if body.get('object') == 'instagram':
                for entry in body['entry']:
                    messaging_events = entry.get('messaging', [])
                    for event in messaging_events:
                        sender_id = event['sender']['id']
                        message_text = event['message'].get('text', '')

                        response = "This is a response"
                        send_customer_a_message(PAGE_ID, response, PAGE_ACCESS_TOKEN, sender_id)
                return make_response('EVENT_RECEIVED', 200)
            else:
                return make_response('Not Found', 404)
        except Exception as e:
            return make_response('Internal Server Error', 500)

def send_customer_a_message(page_id, response, page_token, psid):
    url = (
        f"https://graph.facebook.com/v14.0/{page_id}/messages"
        f"?recipient={{\"id\":\"{psid}\"}}"
        f"&message={{\"text\":\"{response}\"}}"
        f"&messaging_type=RESPONSE"
        f"&access_token={page_token}"
    )

    try:
        response = requests.post(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return {}

@app.route('/update-tokens', methods=['POST'])
def update_tokens():
    data = request.get_json()
    global VERIFY_TOKEN, PAGE_ID, PAGE_ACCESS_TOKEN
    
    verify_token = data.get('VERIFY_TOKEN')
    page_id = data.get('PAGE_ID')
    page_access_token = data.get('PAGE_ACCESS_TOKEN')
    
    if verify_token and page_id and page_access_token:
        VERIFY_TOKEN = verify_token
        PAGE_ID = page_id
        PAGE_ACCESS_TOKEN = page_access_token
        return make_response('Tokens updated successfully', 200)
    return make_response('Bad Request', 400)

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)