import socket
from  threading import Thread
import time

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


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
            else:
                removeClient(client_name)

        except:
            pass


def removeClient(client_name):
    try:
        if  client_name in CLIENTS:
            del CLIENTS[client_name]
    except KeyError:
        pass


def handleSendFile(client_name, file_name, file_size):
    global CLIENTS
    
    CLIENTS[client_name]["fileName"] = file_name
    CLIENTS[client_name]["fileSize"] = file_size

    otherClientName = CLIENTS[client_name]['connectedWith']
    otherClientSocket = CLIENTS[otherClientName]['client']

    msg = f'\n{client_name} want to send {file_name} file with size {file_size} bytes. Do you want to download? y/n'
    otherClientSocket.send(msg.encode())

    time.sleep(1)

    msg2 = f'Download: {file_name}'
    otherClientSocket.send(msg2.encode())


def grantAccess(client_name):
    global CLIENTS

    otherClientName = CLIENTS[client_name]['connectedWith']
    otherClientSocket = CLIENTS[otherClientName]['client']

    msg = '!access granted!'
    otherClientSocket.send(msg.encode())


def declineAccess(client_name):
    global CLIENTS

    otherClientName = CLIENTS[client_name]['connectedWith']
    otherClientSocket = CLIENTS[otherClientName]['client']

    msg = '!access declined!'
    otherClientSocket.send(msg.encode())


def sendTextMsg(client_name, message):
    global CLIENTS

    otherClientName = CLIENTS[client_name]['connectedWith']
    otherClientSocket = CLIENTS[otherClientName]['client']

    msg = client_name+": "+ message
    otherClientSocket.send(msg.encode())



def handleErrorMesssage(client):
    msg = '''
    You need to connect with one of the client first before sending any message.
    Click on Refresh to see all available users.
    '''
    client.send(msg.encode())


def handleMsgs(client, message, client_name):
    if message == "show list":
        handleShowlist(client)

    elif message[:7] == "connect":
        connectClient(message, client, client_name)

    elif message[:10] == "disconnect":
        disconnectClient(message, client, client_name)

    elif message[:4] == 'send':
        file_name = message.split(' ')[1]
        file_size = int(message.split(' ')[2])
        handleSendFile(client_name, file_name, file_size)
        print(client_name, file_name, file_size)
    
    elif message == 'y' or message == 'Y':
        grantAccess(client_name)

    elif message == 'n' or message == "N":
        declineAccess(client_name)

    else:
        connected = CLIENTS[client_name]['connectedWith']
        if connected:
            sendTextMsg(client_name, message)
        else:
            handleErrorMesssage(client)

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


def ftp():
    global IP_ADDRESS
    authorizer = DummyAuthorizer()
    authorizer.add_user("abcde", "abcde", ".", perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    ftp_server = FTPServer((IP_ADDRESS, 21), handler)
    ftp_server.serve_forever()


thread1 = Thread(target = setup)
thread1.start()

thread2 = Thread(target = ftp)
thread2.start()
