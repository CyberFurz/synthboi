import os
from flask import Flask, jsonify, request
from time import sleep
from waitress import serve
from mastodon import Mastodon
from functools import wraps
from threading import Thread

# Get Mastodon API URL and Access Token from environment variables
MastodonURL = os.environ.get('MASTODON_API_URL')
MastodonToken = os.environ.get('MASTODON_ACCESS_TOKEN')
APIKey = os.environ.get('API_KEY') # this is your custom API key for authorization
PORT = os.environ.get('PORT', 5000)

# Create Flask app
app = Flask(__name__)

# Create Mastodon API instance
mastodon = Mastodon(access_token = MastodonToken, api_base_url = MastodonURL)

# Get all active local users
def get_all_users():
    accounts = []
    max_id = None
    while True:
        response = mastodon.admin_accounts_v2(origin='local', status='active', max_id=max_id)
        accounts.extend(response)

        if len(response) > 0:
            max_id = response[-1]['id']
        else:
            break

    users = [user['account']['acct'] for user in accounts]
    return users

# Send a message to a list of users
def send_messages(users, message):
    for user in users:
        mastodon.status_post(f'@{user} {message}', visibility='direct')
        sleep(5) # sleep for 5 seconds to avoid rate limiting

# Custom authorization decorator
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the header is present
        if 'Authorization' not in request.headers:
            return jsonify(message='Unauthorized'), 401

        # Check the value of the Authorization header
        # Implement your custom authorization logic here
        auth_value = request.headers['Authorization']
        if auth_value != APIKey:
            return jsonify(message='Unauthorized'), 401

        return f(*args, **kwargs)
    return decorated_function

# Default route
@app.route('/')
def index():
    return jsonify(message='You should not be here')

# Send a message to a new user upon approval webhook
@app.route('/newuser', methods=['POST'])
def webhook():
    data=request.json
    if 'secret' in data:
        if request.json['secret'] == 'leve-me-alone':
            user = request.json['username']
            message = "Welcome! Your home feed might be looking a bit empty, let us fix that! Learn how to follow tags here: https://hack13.link/follow-tags \n We suggest following #furry #furryart #vrchat \n Hope you enjoy your stay!"
            thread = Thread(target=send_messages, args=([user], message))
            thread.start()
            return jsonify(success=True)
        else:
            return jsonify(success=False,error='Wrong secret')
    else:
        return jsonify(success=False,error='No secret provided')
    
@app.route('/getallusers', methods=['GET'])
@authorize
def getallusers():
    users = get_all_users()
    return jsonify(users)

# Send a message to all active local users
@app.route('/massmessage', methods=['POST'])
@authorize
def massmessage():
    data=request.json
    if 'message' in data:
        users = get_all_users()
        message = data['message']
        thread = Thread(target=send_messages, args=(users, message))
        thread.start()
        return jsonify(success=True)
    else:
        return jsonify(success=False,error='No message provided')
    
# Send a direct message to a specifc local user
@app.route('/singlemessage', methods=['POST'])
@authorize
def singlemessage():
    data=request.json
    if 'message' in data:
        user = data['username']
        message = data['message']
        thread = Thread(target=send_messages, args=([user], message))
        thread.start()
        return jsonify(success=True)
    else:
        return jsonify(success=False,error='No message provided')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=PORT)