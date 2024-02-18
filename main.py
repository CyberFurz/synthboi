import os
import re
from matrixSignup import *
from flask import Flask, jsonify, request, redirect
from flask_cors import cross_origin
from time import sleep
from waitress import serve
from mastodon import Mastodon
from functools import wraps
from threading import Thread
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

# Get Mastodon API URL and Access Token from environment variables
MastodonURL = os.environ.get("MASTODON_API_URL")
MastodonToken = os.environ.get("MASTODON_ACCESS_TOKEN")
APIKey = os.environ.get("API_KEY")  # this is your custom API key for authorization
ThreadsClientID = os.environ.get("THREADS_CLIENT_ID")  # for the threads domain block
ThreadsClientSecret = os.environ.get(
    "THREADS_CLIENT_SECRET"
)  # for the threads domain block
ServerAddress = os.environ.get("SERVER_ADDRESS")  # for the threads domain block
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS").split(",")
PORT = os.environ.get("PORT", 5000)


# Check for valid email address
def check_email(email):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False


# Create Flask app
app = Flask(__name__)

# Create Mastodon API instance
mastodon = Mastodon(access_token=MastodonToken, api_base_url=MastodonURL)

# For blocking threads.net custom client
mastodon_client = Mastodon(
    api_base_url=MastodonURL,
    client_id=ThreadsClientID,
    client_secret=ThreadsClientSecret,
)


# Get all active local users
def get_all_users():
    accounts = []
    max_id = None
    while True:
        response = mastodon.admin_accounts_v2(
            origin="local", status="active", max_id=max_id
        )
        accounts.extend(response)

        if len(response) > 0:
            max_id = response[-1]["id"]
        else:
            break

    users = [user["account"]["acct"] for user in accounts]
    return users


# Send a message to a list of users
def send_messages(users, message):
    for user in users:
        mastodon.status_post(f"@{user} {message}", visibility="direct")
        sleep(5)  # sleep for 5 seconds to avoid rate limiting


# Custom authorization decorator
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the header is present
        if "Authorization" not in request.headers:
            return jsonify(message="Unauthorized"), 401

        # Check the value of the Authorization header
        # Implement your custom authorization logic here
        auth_value = request.headers["Authorization"]
        if auth_value != APIKey:
            return jsonify(message="Unauthorized"), 401

        return f(*args, **kwargs)

    return decorated_function


# Default route
@app.route("/")
def index():
    return jsonify(message="You should not be here")


# matrix signup
@app.route("/createMatrixUser", methods=["POST"])
@cross_origin(origins=[ALLOWED_ORIGINS])
def createMatrixUser():
    data = request.json
    if "username" in data:
        user = data["username"]
        acceptedTOS = data["termsAccepted"]
        password = data["password"]
        displayName = data["displayName"]
        email = data["email"]
        if acceptedTOS == False:
            return jsonify(success=False, error="You must accept the terms of service")
        if check_email(email) == False:
            return jsonify(success=False, error="Invalid email address")
        creationMessage = create_user_account(user, password, displayName, email)
        if creationMessage == 0:
            return jsonify(success=True, message="User account created sucessfully")
        elif creationMessage == 1:
            return jsonify(success=False, error="There was an error creating the User")
        else:
            return jsonify(success=False, error="The user name is taken")
    else:
        return jsonify(success=False, error="There was an error")


# Send a message to a new user upon approval webhook
@app.route("/newuser", methods=["POST"])
def webhook():
    data = request.json
    if "secret" in data:
        if request.json["secret"] == "leve-me-alone":
            user = request.json["username"]
            message = "Welcome! Your home feed might be looking a bit empty, let us fix that! Learn how to follow tags here: https://hack13.link/follow-tags \n We suggest following #furry #furryart #vrchat \n Hope you enjoy your stay!"
            thread = Thread(target=send_messages, args=([user], message))
            thread.start()
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Wrong secret")
    else:
        return jsonify(success=False, error="No secret provided")


@app.route("/getallusers", methods=["GET"])
@authorize
def getallusers():
    users = get_all_users()
    return jsonify(users)


# Send a message to all active local users
@app.route("/massmessage", methods=["POST"])
@authorize
def massmessage():
    data = request.json
    if "message" in data:
        users = get_all_users()
        message = data["message"]
        thread = Thread(target=send_messages, args=(users, message))
        thread.start()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="No message provided")


# Send a direct message to a specifc local user
@app.route("/singlemessage", methods=["POST"])
@authorize
def singlemessage():
    data = request.json
    if "message" in data:
        user = data["username"]
        message = data["message"]
        thread = Thread(target=send_messages, args=([user], message))
        thread.start()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="No message provided")


# Block federation with Threads by meta
@app.route("/blockthreads", methods=["GET"])
def blockthreads():
    testing = mastodon_client.auth_request_url(
        client_id=ThreadsClientID,
        redirect_uris=f"{ServerAddress}/callback",
        scopes=["read:blocks", "write:blocks"],
    )

    return redirect(testing)


# Block spam tags
@app.route("/blockspam", methods=["GET"])
def blockspam():
    flowstate = mastodon_client.auth_request_url(
        client_id=ThreadsClientID,
        redirect_uris=f"{ServerAddress}/callback-spam",
        scopes=["read:filters", "write:filters"],
    )

    return redirect(flowstate)


# Block federation with Threads by meta callback
@app.route("/callback", methods=["GET"])
def blockthreadscallback():
    if "code" not in request.args:
        return jsonify(success=False, error="No code provided")
    else:
        logged_in_client = mastodon_client.log_in(
            code=request.args.get("code"),
            redirect_uri=f"{ServerAddress}/callback",
            scopes=["read:blocks", "write:blocks"],
        )
        logged_in_client = Mastodon(
            access_token=logged_in_client, api_base_url=MastodonURL
        )
        logged_in_client.domain_block(domain="threads.net")
        return jsonify(success=True)


# Block spam tags callback
@app.route("/callback-spam", methods=["GET"])
def blockspamcallback():
    if "code" not in request.args:
        return jsonify(success=False, error="No code provided")
    else:
        spam_tags = ["#診断メーカー"]
        logged_in_client = mastodon_client.log_in(
            code=request.args.get("code"),
            redirect_uri=f"{ServerAddress}/callback-spam",
            scopes=["read:filters", "write:filters"],
        )
        logged_in_client = Mastodon(
            access_token=logged_in_client, api_base_url=MastodonURL
        )
        for tag in spam_tags:
            logged_in_client.filter_create(
                context=["home", "notifications", "public", "thread"],
                phrase=tag,
                irreversible=False,
                whole_word=True,
                expires_in=None,
            )
        return jsonify(success=True)


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=PORT)
