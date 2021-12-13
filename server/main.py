import asyncio
import websockets
import random
import time

serveip = "brug"

message_log = {}
users = {}
bans = {}

with open("message.txt", "r") as f:
    message_log = eval(f.read())
with open("users.txt", "r") as f:
    users = eval(f.read())
with open("bans.txt", "r") as f:
    bans = eval(f.read())

style = '<span class="mes" style="background-color: '
motd = "Welcome to the WLC!"

# -- ADMIN COMMANDS --#
def processAdminCommands(message, chan):
    global message_log
    global admin_name
    global bans
    global users

    if message[0] == "/say":
        print(message[1])
        message_log[chan].append('<span style="font-size: 30px;">'+"|".join([i for i in message[1:]])+"</span>")
    elif message[0] == "/clear":
        if message[1] == "mes":
            del message_log[chan][int(message[2])]
        elif message[1] == "color":
            users = {}
        elif message[1] == "chan":
            message_log[chan] = []
        elif message[1] == "has":
            message_log[chan] = [i for i in message_log if i.find(message[2]) == -1]
        elif message[1] == "all":
            message_log = {}
    elif message[0] == "/run":
        exec(message[1])
    elif message[0] == "/edit":
        message_log[chan][int(message[1])] = message_log[int(message[1])][:len(style)+10] + message[2] + "</span>"
    elif message[0] == "/embed":
        message_log[chan].append(message[1].replace("&lt;", "<").replace("&gt;", ">"))
    elif message[0] == "/color":
        users[message[1]]["color"] = message[2]
    elif message[0] == "/ban":
        bans[message[1]] = message[2]
    elif message[0] == "/ip":
        print("\n")
        found = 0
        for key, value in users.items():
            if value["name"] == message[1]:
                print(f"Name: {value['name']}, IP: {key}")
                found = 1
        if not found:
            print(f"Could not find any users with name: {message[1]}")
        print("\n")
    elif message[0] == "/clean_channels":
        empty_keys = []
        for key, value in message_log.items():
            if value == []:
                empty_keys.append(key)
        for i in empty_keys:
            del message_log[i]
    else:
        print("Command error: " + str(message))
# -- ADMIN COMMANDS --#

# -- USER COMMANDS --#
def processUserCommands(message, color, name):
    if message[0][0] == "/":
        if message[0] == "/img":
            message_log.append(style + color + ';">' + name + ": </span><br>" + "<img src='" + message[1] + "' style='background-color: " + color + "; padding: 5px; border-radius: 5px; max-width: 500px; max-height: 700px; width: auto; height: auto;' /img>")
        else:
            return False
    else:
        return True
# -- USER COMMANDS --#

#if len(message_log) == 0:
#    processAdminCommands(["/say", motd])

async def getMessage(websocket, path):
    global message_log
    
    prot = "NONE"
    try: 
        prot = await websocket.recv()
    except BaseException as e:
        print(f"\n -- ERROR -- \n{e}\n")
    
    ip = websocket.remote_address[0]
    
    if prot == "POST" and not (ip in bans):
        name = (await websocket.recv()).replace("<", "&lt;").replace(">", "&gt;")
        message = (await websocket.recv()).replace("<", "&lt;").replace(">", "&gt;")
        channel = await websocket.recv()
        
        if not channel in message_log:
            message_log[channel] = []
        
        if message[-1] == "\n":
            message = message[:-1]
        print(name, message, channel)
        
        if not (ip in users):
            users[ip] = {"color": "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]), "last get": time.time()}
        users[ip]["name"] = name

        color = users[ip]["color"]
        command_result = processUserCommands(message.split("|"), color, name)
        if command_result == True:
            message_log[channel].append(style + color + ';">' + name + ": " + message + "</span>")
        elif message[0] == "/" and ip == serveip:
            processAdminCommands(message.split("|"), channel)
        
    elif prot == "GET":
        channel = await websocket.recv()
        
        if not channel in message_log:
            message_log[channel] = []
        
        if ip in bans:
            await websocket.send("You have been banned for: " + bans[ip])
        else:
            if ip in users:
                users[ip]["last get"] = time.time()
            await websocket.send("<br>".join(message_log[channel]))
        with open("users.txt", "w") as f:
            f.write(str(users))
    elif prot == "ONLINE":
        online = []
        for ip, info in users.items():
            if "last get" in info:
                if (time.time() - info["last get"]) < 5:
                    online.append(style + info["color"] + ';">' + info["name"] + "</span>")
        await websocket.send("<br>".join(online))
        
    with open("message.txt", "w") as f:
        f.write(str(message_log))
    with open("users.txt", "w") as f:
        f.write(str(users))
    with open("bans.txt", "w") as f:
        f.write(str(bans))

start_server = websockets.serve(getMessage, serveip, 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()