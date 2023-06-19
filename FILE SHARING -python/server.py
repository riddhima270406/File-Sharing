import socket
from  threading import Thread
import time

SERVER = None
PORT = None
IP_ADDRESS = None

bufferSize = 4096

CLIENTS = {}

def handleClient(client, client_name):
    global CLIENTS, SERVER, bufferSize

    banner1 = "Welcome, You are now connected to Server!\nClick on Refresh to see all available users.\nSelect the user and click on Connect to start chatting."

    client.send(banner1.encode())

    while True:
        try:
            bufferSize = CLIENTS[client_name]["fileSize"]
            chunk = client.recv(bufferSize)
            message = chunk.decode().strip().lower()
            if message:
                handleMsgs(client, message, client_name)

        except:
            pass


def handleMsgs(client, message, client_name):
    if message == "show list":
        handleShowlist(client)
    elif message[:7] == "connect":
        connectClient(message, client, client_name)
    elif message[:10] == "disconnect":
        disconnectClient(message, client, client_name)


def handleShowlist(client):
    global CLIENTS
    counter = 0
    for i in CLIENTS:
        counter += 1
        clientAddress = CLIENTS[i]['address'][0]
        connectedWith = CLIENTS[i]['connectedWith']
        message = ''
        if connectedWith:
            message = f"{counter}, {i}, {clientAddress}, connected With: {connectedWith}, tiul \n"
        else:
            message = f"{counter}, {i}, {clientAddress}, available, tiul \n"
        client.send(message.encode())



def connectClient(message, client, client_name):
    global CLIENTS
    enterCN = message[8:].strip()
    if enterCN in  CLIENTS:
        if not CLIENTS[client_name]["connectedWith"]:
            CLIENTS[enterCN]["connectedWith"] = client_name
            CLIENTS[client_name]["connectedWith"] = enterCN
            otherCsocket = CLIENTS[enterCN]['client']
            msg = f'hello, {enterCN} {client_name} connected with you!'
            otherCsocket.send(msg.encode())
            msg2 = f'you are successfully connected with {enterCN}'
            client.send(msg2.encode())
        else:
            otherCname = CLIENTS[client_name]['connectedWith']
            msg = f'you are already connected with {otherCname}'
            client.send(msg.encode())



def disconnectClient(message, client, client_name):
    global CLIENTS
    enterCN = message[11:].strip()
    if enterCN in CLIENTS:
        CLIENTS[enterCN]["connectedWith"] = ''
        CLIENTS[client_name]["connectedWith"] = ''
        otherCsocket = CLIENTS[enterCN]['client']
        msg = f'hello, {enterCN}, you are disconnected with {client_name}'
        otherCsocket.send(msg.encode())
        msg2 = f'you are successfully disconnected with {enterCN}'
        client.send(msg2.encode())




def acceptConnections():
    global SERVER, CLIENTS
    while True:
        client, addr = SERVER.accept()
        print(client, addr)

        client_name = client.recv(1024).decode().strip()

        CLIENTS[client_name] = {
            'client': client,
            'address': addr,
            'connectedWith': '',
            'fileName': '',
            'fileSize': 4096
        }

        print(f"Connection established with {client_name} : {addr}")

        thread = Thread(target = handleClient, args=(client,client_name,))
        thread.start()

    

def setup():
    print("\n")
    print("****   FILE SHARING   ****   ")


    global SERVER
    global PORT
    global IP_ADDRESS

    IP_ADDRESS = '127.0.0.1'
    PORT = 8000
    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.bind((IP_ADDRESS, PORT))

    SERVER.listen(10)

    print("SERVER IS WAITING FOR INCOMMING CONNECTIONS...")
    print("\n")


    acceptConnections()


thread1 = Thread(target = setup)
thread1.start()