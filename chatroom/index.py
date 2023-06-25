import asyncio
import json
from request import request
from js import Blob, URL
from datetime import datetime

username = "user"
userrole = ""
roomcode = ""
url = "https://rahul-s-database-default-rtdb.firebaseio.com/chatroom.json" # chat room (json)

async def updatemessage(): # update new message
    while(1):
        chatroom = await request(url, asjson=True)
        message_q = chatroom["rooms"][roomcode]["message_queue"]

        while(len(message_q) > 1):
            for m in message_q.pop(1).items():
                Element("livemsg").element.innerHTML += "<p>"+m[0]+":"+m[1]+"</p>"
                newmsg = {m[0]:m[1]}
            Element("displayerror").element.innerText = ""

            chatroom["rooms"][roomcode]["messages"].append(newmsg)

            chatroom = json.dumps(chatroom)
            await request(url, body=chatroom, method="PUT")

            await asyncio.sleep(0)
        await asyncio.sleep(0)

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

async def create(): # create a room

    chatroom = await request(url, asjson=True)

    global roomcode
    global userrole
    roomcode = Element("textfield").element.value # user entered room code

    if(roomcode in chatroom["rooms"]): # display error if room already exist
        Element("textfield").element.value = ""
        Element("displayerror").element.innerText = "Room already exist"

    elif((len(roomcode) == 7 and roomcode[5:] == "-p" in roomcode) or len(roomcode) == 5): # create a room

        userrole = "owner"
        # update buttons

        Element("cnt").element.remove()
        Element("create").element.remove()
        Element("send").element.removeAttribute("hidden")
        Element("gencf").element.removeAttribute("hidden")

        # room type
        Type = "public"
        if(roomcode[5:] == "-p"):
            Type = "private"
            roomcode = roomcode[:5]

        # new room
        chatroom["rooms"][roomcode] = {"type":Type}
        chatroom["rooms"][roomcode]["message_queue"] = [{"mrnobodyinchat":"This is reserved"}]
        chatroom["rooms"][roomcode]["messages"] = [{"mrnobodyinchat":"Wellcum to"+roomcode}]
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

        Element("displayerror").element.innerText = ""
        Element("body").element.removeAttribute("py-click")
        Element("displayerror").element.removeAttribute("py-mouseover")
        Element("displayerror").element.removeAttribute("py-mouseout")

        callasyncfunc("updatemessage()")

    else: # display error if roomcode is empty
        Element("displayerror").element.innerText = "Enter a 5 character roomcode"

async def connect(): # join a room
    chatroom = await request(url, asjson=True)

    global roomcode
    global userrole
    roomcode = Element("textfield").element.value # user entered room code

    if(roomcode not in chatroom["rooms"]): # display error if room not exist
        Element("textfield").element.value = ""
        Element("displayerror").element.innerText = "Room does not exist"

    else: # join a room

        userrole = "member"

        # update buttons
        Element("cnt").element.remove()
        Element("create").element.remove()
        Element("send").element.removeAttribute("hidden")

        # update text field
        Element("textfield").element.value = ""
        Element("textfield").element.placeholder = "messages"
        
        # update room
        chatroom["rooms"][roomcode]["participants"] += 1
        chatroom["rooms"][roomcode]["participants_list"].append(username)

        newroom = json.dumps(chatroom)
        await request(url, body=newroom, method="PUT")

        Element("cntto").element.innerText = "Connected to "+roomcode

        Element("displayerror").element.innerText = ""
        Element("body").element.removeAttribute("py-click")
        Element("displayerror").element.removeAttribute("py-mouseover")
        Element("displayerror").element.removeAttribute("py-mouseout")

        callasyncfunc("updatemessage()")

async def send(): # send a message
    Element("displayerror").element.innerText = "sending..."
    chatroom = await request(url, asjson=True)
    
    chatroom["rooms"][roomcode]["message_queue"].append({username:Element("textfield").element.value})
    
    newmessage = json.dumps(chatroom)
    await request(url, body=newmessage, method="PUT")

    Element("textfield").element.value = ""

async def delete_data(): # delete all data of the user
    chatroom = await request(url, asjson=True)
    if(username in chatroom["general"]["user_list"]):
        chatroom["general"]["user_list"].remove(username)
        chatroom["general"]["total_users"] -= 1
        
        if(roomcode in chatroom["rooms"]):
            if(userrole == "owner"):
                chatroom["general"]["room_list"].remove(roomcode)
                chatroom["general"]["total_rooms"] -= 1
                chatroom["rooms"].pop(roomcode)
        
            chatroom["rooms"][roomcode]["participants_list"].remove(username)
            chatroom["rooms"][roomcode]["participants"] -= 1
        chatroom = json.dumps(chatroom)
        await request(url, body=chatroom, method="PUT")
    chatroom["rooms"]["reloaded"] = True
    chatroom = json.dumps(chatroom)
    await request(url, body=chatroom, method="PUT")

async def gen_ctxtf():
    messages = await request(url, asjson=True)
    messages = messages["rooms"][roomcode]["messages"]
    chat = []
    for i in messages:
        for m in i.items():
            chat.append(m[0]+":"+m[1])
    filelink = Element("filelink")
    file = Blob([chat], {type:"text/plain"})
    filelink.element.href = URL.createObjectURL(file)
    filelink.element.download = "Chats.txt"
    filelink.element.click()
    URL.revokeObjectURL(filelink.element.href)

    Element("gencf").element.remove()

def callasyncfunc(funcname):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(eval(funcname))

# remove error message
erase = True
def keeperror():
    global erase
    erase = False

def eraseerror():
    erase = True

def clearerror():
    if(erase):
        Element("displayerror").element.innerText = ""