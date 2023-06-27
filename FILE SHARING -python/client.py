import socket
from tkinter import *
from  threading import Thread
import random
from PIL import ImageTk, Image
from tkinter import ttk

import os
import ftplib
import ntpath
from ftplib import FTP
from pathlib import Path
from tkinter import filedialog

SERVER = None
PORT = None
IP_ADDRESS = None

bufferSize = 4096

name = None
listBox = None
textArea = None
labelChat = None
textmsg = None

sendingFile = None
downloadingFile = None
fileToDownload = None
filePathLabel = None


def connectToServer():
    global SERVER, PORT, IP_ADDRESS, name

    name1 = name.get()
    SERVER.send(name1.encode())



def showClientList():
    global listBox, SERVER

    listBox.delete(0,'end')
    SERVER.send('show list'.encode('ascii'))


def connectWithClient():
    global SERVER, listBox

    text = listBox.get(ANCHOR)
    lisItem = text.split(':')
    msg = "connect "+ lisItem[1]
    SERVER.send(msg.encode('ascii'))


def disconnectWithClient():
    global SERVER, listBox

    text = listBox.get(ANCHOR)
    lisItem = text.split(':')
    msg = "disconnect "+ lisItem[1]
    SERVER.send(msg.encode('ascii'))
    


def openChatWindow():
    global name, listBox, textArea, labelChat, textmsg, filePathLabel

    root = Tk()
    root.title("Chat Window")
    root.geometry("500x350")

    nameLabel = Label(root, text="Enter your name: ", font=('Calibri', 10))
    nameLabel.place(x=10, y=8)

    name = Entry(root, width=30, font=('Calibri', 10))
    name.place(x=120, y=8)
    name.focus()

    connectServer = Button(root, text="CONNECT TO CHAT SERVER", font=('Calibri', 10), bd = 1, command=connectToServer)
    connectServer.place(x=344, y=6)

    seperator = ttk.Separator(root, orient='horizontal')
    seperator.place(x=0, y=35, relwidth=1, height=0.1)

    labelUsers = Label(root, text="ACTIVE USERS", font=('Calibri', 10))
    labelUsers.place(x=10, y=50)

    listBox = Listbox(root, height=5, width=67, font=('Calibri', 10))
    listBox.place(x=10, y=70)

    scrollbar1 = Scrollbar(listBox)
    scrollbar1.place(relheight=1, relx=1)
    scrollbar1.config(command=listBox.yview)

    connectButton = Button(root, text="CONNECT", bd=1, font=('Calibri', 10), command=connectWithClient)
    connectButton.place(x=282, y=160)

    disconnectButton = Button(root, text="DISCONNECT", bd=1, font=('Calibri', 10), command=disconnectWithClient)
    disconnectButton.place(x=350, y=160)

    refreshButton = Button(root, text="REFRESH", bd=1, font=('Calibri', 10), command=showClientList)
    refreshButton.place(x=435, y=160)

    labelChat = Label(root, text="CHAT WINDOW", font=('Calibri', 10))
    labelChat.place(x=10, y=180)

    textArea = Text(root, height=6, width=67, font=('Calibri', 10))
    textArea.place(x=10, y=200)

    scrollbar2 = Scrollbar(textArea)
    scrollbar2.place(relheight=1, relx=1)
    scrollbar2.config(command=textArea.yview)

    attachButton = Button(root, text="ATTACH & SEND", bd=1, font=('Calibri', 10), command=browseFiles)
    attachButton.place(x=10, y=305)

    textmsg = Entry(root, width=43, font=('Calibri', 10))
    textmsg.place(x=110, y=306)

    sendButton = Button(root, text="SEND", bd=1, font=('Calibri', 10), command=sendMsg)
    sendButton.place(x=450, y=305)
    
    filePathLabel = Label(root, text='', fg='blue', font=('Calibri', 10))
    filePathLabel.place(x=10, y=330)

    root.resizable(False, False)
    root.mainloop()



def getFileSize(fileName):
    with open(fileName, 'rb') as File:
        chunk = File.read()
        return len(chunk)



def browseFiles():
    global sendingFile, textArea, filePathLabel

    try:
        fileName = filedialog.askopenfilename()
        filePathLabel.configure(text=fileName)
        userName = "abcde"
        password = "abcde"
        hostName = "127.0.0.1"

        ftpSERVER = ftplib.FTP(hostName, userName, password)
        ftpSERVER.encoding = 'utf-8'
        ftpSERVER.cwd('shared_files')
        fName = ntpath.basename(fileName)

        with open (fileName, 'rb') as File:
            ftpSERVER.storbinary(f'STOR {fName}', File)
        
        ftpSERVER.dir()
        ftpSERVER.quit()

        message = "send "+fName

        if message[:4] == 'send':
            print("PLEASE WAIT...\n")
            textArea.insert(END, '\nPLEASE WAIT...\n')
            textArea.see('end')
            sendingFile = message[5:]
            fileSize = getFileSize('shared_files/'+sendingFile)
            finalMsg = message+' '+str(fileSize)
            SERVER.send(finalMsg.encode())
            textArea.insert(END, 'in process...')


    except FileNotFoundError:
        print("CANCEL BUTTON PRESSED")




def sendMsg():
    global SERVER, textArea, textmsg, fileToDownload

    msgToSend = textmsg.get()
    SERVER.send(msgToSend.encode('ascii'))
    textArea.insert(END, '\nYou: '+msgToSend)
    textArea.see('end')
    textmsg.delete(0, 'end')

    if msgToSend == 'y' or msgToSend == 'Y':
        textArea.insert(END, '\nPlease wait, the file is downloading...')
        textArea.see('end')
        userName = "abcde"
        password = "abcde"
        hostName = "127.0.0.1"
        home = str(Path.home())

        downloadPath = home+'\Downloads'

        ftpSERVER = ftplib.FTP(hostName, userName, password)
        ftpSERVER.encoding = 'utf-8'
        ftpSERVER.cwd('shared_files')
        fName = fileToDownload
        localFileName = os.path.join(str((downloadPath, fName)))

        file = open(localFileName,'wb')
        ftpSERVER.retrbinary("RETR "+fName,file.write)
        ftpSERVER.dir()
        file.close()
        ftpSERVER.quit()
        print("file downloaded to "+downloadPath)
        textArea.insert(END, '\nFile downloaded to '+downloadPath)
        textArea.see('end')






def recivedMsg():
    global SERVER
    global name
    global textArea
    global bufferSize
    global listBox
    global labelChat
    global downloadingFile

    while True:
        chunk = SERVER.recv(bufferSize)
        try:
            if "tiul" in chunk.decode() and "1.0," not in chunk.decode():
                letterList = chunk.decode().split(',')
                listBox.insert(letterList[0], letterList[0]+': '+letterList[1]+': '+letterList[3])
                print(letterList[0], letterList[0]+': '+letterList[1]+': '+letterList[3])

            elif chunk.decode() == '!access granted!':
                labelChat.configure(text='')
                textArea.insert(END, '\n'+chunk.decode('ascii'))
                textArea.see('end')

            elif chunk.decode() == '!access declined!':
                labelChat.configure(text='')
                textArea.insert(END, '\n'+chunk.decode('ascii'))
                textArea.see('end')

            elif 'download?' in chunk.decode():
                downloadingFile = chunk.decode('ascii').split(' ')[4].strip()
                bufferSize = int(chunk.decode('ascii').split(' ')[8])
                textArea.insert(END, '\n'+chunk.decode('ascii'))
                textArea.see('end')

            elif 'Download:' in chunk.decode():
                getFileName = chunk.decode().split(':')
                fileToDownload = getFileName[1]
                

            else:
                textArea.insert(END, '\n'+chunk.decode('ascii'))
                textArea.see('end')
                print(chunk.decode('ascii'))

        except:
            pass


def setup():
    global SERVER
    global PORT
    global IP_ADDRESS

    PORT  = 8000
    IP_ADDRESS = '127.0.0.1'

    SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER.connect((IP_ADDRESS, PORT))

    thread = Thread(target=recivedMsg)
    thread.start()

    openChatWindow()




setup()
