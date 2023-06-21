import asyncio
import json
from request import request
import threading

username = "user"
url = "https://rahul-s-database-default-rtdb.firebaseio.com/chatroom.json" # chat room (json)

async def setname(): # set user name
    global username
    textfiled = Element("textfield").element.value # user entered name

    chatroom = await request(url, asjson=True) # json general data
    general = chatroom["general"]
    userid = general["total_users"]

    if(textfiled == ""): # default username if field is empty
        username+=str(userid)
        Element("uname").element.innerText = "Username: "+username

        # updated new user to json data base
        chatroom["general"]["total_users"] += 1
        chatroom["general"]["user_list"].append(username)
        newuser = json.dumps(chatroom)
        await request(url, body=newuser, method="PUT")

        # update text field and button for create and join room
        Element("textfield").element.value = ""
        Element("textfield").element.placeholder = "Type a 5 character code to create(add -p at end to make room private) or join a room"

        Element("setname").element.remove()
        Element("cnt").element.style.visibility = "visible"
        Element("create").element.style.visibility = "visible"

    elif(len(textfiled) < 4 or len(textfiled) > 10): # user name character limit
        Element("displayerror").element.innerText = "User name should be atleast 4 character long and atmost 10 character long"
    
    elif(textfiled in general["user_list"]): # display error if username already taken
        Element("displayerror").element.innerText = "User name already in use!"

    else: # set username
        # update text field and button for create and join room
        Element("textfield").element.value = ""
        Element("textfield").element.placeholder = "Type a 5 character code to create or join a room"

        Element("setname").element.remove()
        Element("cnt").element.style.visibility = "visible"
        Element("create").element.style.visibility = "visible"

        # updated new user to json data base
        username=textfiled
        Element("uname").element.innerText = "Username: "+username

        chatroom["general"]["total_users"] += 1
        chatroom["general"]["user_list"].append(username)
        newuser = json.dumps(chatroom)
        await request(url, body=newuser, method="PUT")


def callsetname():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setname())

async def create(): # create a room

    chatroom = await request(url, asjson=True)

    roomcode = Element("textfield").element.value # user entered room code

    if(roomcode in chatroom["rooms"]): # display error if room already exist
        Element("textfield").element.value = ""
        Element("displayerror").element.innerText = "Room already exist"

    elif((len(roomcode) == 7 and roomcode[5:] == "-p" in roomcode) or len(roomcode) == 5): # create a room

        # update buttons

        Element("cnt").element.remove()
        Element("create").element.remove()
        Element("send").element.removeAttribute("hidden")

        # room type
        Type = "public"
        if(roomcode[5:] == "-p"):
            Type = "private"
            roomcode = roomcode[:5]

        # new room
        chatroom["rooms"][roomcode] = {"type":Type}
        chatroom["rooms"][roomcode]["message_queue"] = ["none"]
        chatroom["rooms"][roomcode]["messages"] = ["none"]
        chatroom["rooms"][roomcode]["participants"] = 1
        chatroom["rooms"][roomcode]["participants_list"] = [username]
        chatroom["rooms"][roomcode]["kick_list"] = ["none"]
        chatroom["rooms"][roomcode]["ban_list"] = ["none"]

        chatroom["general"]["total_rooms"] += 1
        chatroom["general"]["room_list"].append(roomcode)
        
        newroom = json.dumps(chatroom)
        await request(url, body=newroom, method="PUT")

        Element("cntto").element.innerText = "Connected to "+roomcode

        # update text field

        Element("textfield").element.value = ""
        Element("textfield").element.placeholder = "messages"

    else: # display error if roomcode is empty
        Element("displayerror").element.innerText = "Enter a 5 character roomcode"

def callcreate():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create())

async def connect(): # join a room
    chatroom = await request(url, asjson=True)

    roomcode = Element("textfield").element.value # user entered room code

    if(roomcode not in chatroom["rooms"]): # display error if room not exist
        Element("textfield").element.value = ""
        Element("displayerror").element.innerText = "Room does not exist"

    elif(len(roomcode) == 5): # join a room

        # update buttons
        Element("cnt").element.remove()
        Element("create").element.remove()
        Element("send").element.removeAttribute("hidden")
        
        # update room
        chatroom["rooms"][roomcode]["participants"] += 1
        chatroom["rooms"][roomcode]["participants_list"].append(username)

        newroom = json.dumps(chatroom)
        await request(url, body=newroom, method="PUT")

        Element("cntto").element.innerText = "Connected to "+roomcode

        # update text field

        Element("textfield").element.value = ""
        Element("textfield").element.placeholder = "messages"

    else: # display error if roomcode is empty
        Element("displayerror").element.innerText = "Enter a 5 character roomcode"

def callconnect():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect())

async def send(): # send a message
	print("sending")

def callsend():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send())

erase = True
def keeperror(): # keep error message when mouse is over the error message
    global erase
    erase = False

def eraseerror(): # erase error message when mouse is not over the error message
    global erase
    erase = True

def clearerror(): # to clear error
    if(erase):
        Element("displayerror").element.innerText = ""