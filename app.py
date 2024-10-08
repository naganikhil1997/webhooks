from flask import Flask, request, make_response
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load configuration from environment variables
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'hello_1234567')
PAGE_ID = os.getenv('PAGE_ID', 'your_predefined_page_id')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN', 'your_predefined_page_access_token')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)