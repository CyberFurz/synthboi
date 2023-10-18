import os
import requests
import hashlib
import hmac

SYNAPSE_SERVER_URL = os.environ.get('SYNAPSE_SERVER_URL')  # place url in env file
REGISTRATION_SHARED_SECRET = os.environ.get('REGISTRATION_SHARED_SECRET') # using environment var to obscure key


def create_user_account(username, password, displayname):
    try:
        nonce = fetch_nonce()  # Fetch the nonce from the API

        mac = generate_mac(nonce, username, password)  # Generate the mac value

        request_body = {
            "nonce": nonce,
            "username": username,
            "displayname": displayname,
            "password": password,
            "admin": False,
            "mac": mac,
        }

        response = requests.post(
            f"{SYNAPSE_SERVER_URL}/_synapse/admin/v1/register", json=request_body
        )

        # Check the response status and handle accordingly
        return response.status_code
    except Exception as e:
        return e


def fetch_nonce():
    try:
        response = requests.get(f"{SYNAPSE_SERVER_URL}/_synapse/admin/v1/register")
        data = response.json()
        return data["nonce"]
    except Exception as e:
        raise Exception("Failed to fetch nonce")


def generate_mac(nonce, user, password, admin=False, user_type=None):

    mac = hmac.new(
      key=REGISTRATION_SHARED_SECRET,
      digestmod=hashlib.sha1,
    )

    mac.update(nonce.encode('utf8'))
    mac.update(b"\x00")
    mac.update(user.encode('utf8'))
    mac.update(b"\x00")
    mac.update(password.encode('utf8'))
    mac.update(b"\x00")
    mac.update(b"admin" if admin else b"notadmin")
    if user_type:
        mac.update(b"\x00")
        mac.update(user_type.encode('utf8'))

    return mac.hexdigest()