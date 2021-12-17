import socket

HEADER = 64
PORT = 5050
SERVER = "192.168.1.15"
ADDR = (SERVER ,PORT)
FORMAT = 'utf_8'
DISSCONECT_MSG = "Disconnected!"

client = socket.socket(socket.AF_INET ,socket.SOCK_STREAM) #AF :ip v4 sock_stream: TCP
client.connect(ADDR)

def send(msg):
    message =msg.encode(FORMAT)
    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b' ' * (HEADER-len(send_len))

    client.send(send_len)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("Hello world!")
input()
send("Hello Everyone!")
input()
send("Hello Sedky!")

send("Disconnected!")