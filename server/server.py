import socket
import threading # to create multiple threads with one python program

HEADER = 64
PORT = 5050
# server = "192.168.100.54"
SERVER = socket.gethostbyname(socket.gethostname()) #for local network , for global network put global ip address
ADDR = (SERVER ,PORT)
FORMAT = 'utf_8'
DISSCONECT_MSG = "Disconnected!"

server = socket.socket(socket.AF_INET ,socket.SOCK_STREAM) #AF :ip v4 sock_stream: TCP
server.bind(ADDR)

def handleClient(connection , address):
    print (f"[Active Connection:] {address} connection")

    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT) #wait untill sth is sent over the socket (we 'll determine how many bites we will accept)
        if msg_length:
            msg_length =int(msg_length)
            msg =connection.recv(msg_length).decode(FORMAT) # the actual msg
            if(msg == DISSCONECT_MSG):
                connected =False
            print(f"[{address}] {msg}")
            connection.send("Msg Received Porperly!".encode(FORMAT))

    connection.close()

def start(): # it 'll start the socket server for us
    server.listen()
    print (f"[LISTENING] The Server Is Listening On: {SERVER}")
    while True:
        connection ,address = server.accept() # we 'll wait until a new connection occurs and save which address it came from and the acual object 
        thread = threading.Thread(target=handleClient , args=(connection,address))
        thread.start()
        print (f"[ACTIVE CONNECTIONS: ]{threading.active_count() -1}")

print("[STARTING] the server is starting ...")
start()