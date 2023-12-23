import os
import requests

SYNAPSE_SERVER_URL = os.environ.get('SYNAPSE_SERVER_URL')  # place url in env file
ACESS_TOKEN = os.environ.get('LOGIN_ACESS_TOKEN') #needed for sending requests to the api
AuthHeaders = { #generate header for acess
     "Content-Type": "application/json",
     "Authorization": f"Bearer {ACESS_TOKEN}"
}

#creating user function
def create_user_account(username: str, password: str, displayname: str, email_addr: str):
    usrName=f"@{username}:cyberfurz.chat" #formats the username properly for put
    try:
        #check if the username is available
        status = requests.get(f"{SYNAPSE_SERVER_URL}/_synapse/admin/v1/username_available?username={username}", headers=AuthHeaders)
        if( status.status_code == 200):
            #if availble create user json
            request_body = {
            "password": password,
            "logout_devices": False,
            "displayname": displayname,
            "avatar_url": None,
            "threepids": [
                {
                    "medium": "email",
                    "address": email_addr
                }
            ],
            "admin": False,
            "deactivated": False,
            "user_type": None,
            "locked": False
            }
            #variable to hold response
            callCreate = requests.put(f"{SYNAPSE_SERVER_URL}/_synapse/admin/v2/users/{usrName}", headers=AuthHeaders, json=request_body) 
            #resposnse checking
            if(callCreate.status_code == 201):
                #sucess
                 return 0
            else:
                 #vaild  but error occured
                 return 1   
        else:
            #user name taken
            return 2   
    except Exception as e:
        return e
