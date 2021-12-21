from socket import AF_INET, socket, SOCK_STREAM
from cryptography.fernet import Fernet
from threading import Thread
import tkinter
from tkinter import font


def receiveResponse():
    while True:
        try:
            message = receiveMessage()

            msg_list.insert(tkinter.END, message)

            # Scroll to the end of the list
            msg_list.yview(tkinter.END)
            if message == "Connection Timed Out!":
                close()
        except OSError:
            break


def receiveMessage():
    messageLength = client_socket.recv(BUFFERSIZE).decode(FORMAT)

    messageLength = int(messageLength)
    message = client_socket.recv(messageLength).decode(FORMAT)
    return message


def sendResponse(event=None):
    # Get message from input field
    message = inputMessage.get()
    inputMessage.set("")

    sendMessage(message)

    msg_list.insert(tkinter.END, PREFIX + message)

    # Scroll to the end of the list
    # Change text color to blue
    msg_list.yview(tkinter.END)
    msg_list.itemconfig(tkinter.END, foreground="blue")


def sendMessage(message):
    message = encryptMessage(message)

    messageLength = len(message)
    send_len = str(messageLength).encode(FORMAT)
    send_len += b" " * (BUFFERSIZE - len(send_len))

    client_socket.send(send_len)
    client_socket.send(message)

def encryptMessage(message):
    key = loadKey()
    message = message.encode(FORMAT)
    f = Fernet(key)
    encryptedMessage = f.encrypt(message)

    return encryptedMessage

def loadKey():
    return open("key/secret.key", "rb").read()

def close(event=None):
    client_socket.close()
    top.quit()


top = tkinter.Tk()
top.title("Pharmacy Chatbot")

messages_frame = tkinter.Frame(top)
inputMessage = tkinter.StringVar()
inputMessage.set("")
scrollbar = tkinter.Scrollbar(messages_frame)

msg_list = tkinter.Listbox(
    messages_frame,
    height=15,
    width=100,
    yscrollcommand=scrollbar.set,
    font=font.Font(size=18),
)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH, padx=10, pady=10)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=inputMessage, font=font.Font(size=14))
entry_field.bind("<Return>", sendResponse)
entry_field.pack(padx=10, pady=10)
send_button = tkinter.Button(
    top, text="Send", command=sendResponse, font=font.Font(size=14)
)
send_button.pack(padx=10, pady=10)

top.protocol("WM_DELETE_WINDOW", close)

HOST = "localhost"
PORT = 5050
BUFFERSIZE = 64
FORMAT = "utf_8"

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((HOST, PORT))

PREFIX = "You: "

# Handle the client request on a new thread to avoid blocking new requests
receive_thread = Thread(target=receiveResponse)
receive_thread.start()
tkinter.mainloop()
