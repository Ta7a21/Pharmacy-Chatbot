import socket
import threading  # to create multiple threads with one python program

HEADER = 64
PORT = 5050
# server = "192.168.100.54"
SERVER = socket.gethostbyname(
    socket.gethostname()
)  # for local network , for global network put global ip address
ADDR = (SERVER, PORT)
FORMAT = "utf_8"
DISSCONECT_MSG = "close"
PREFIX = "Pharmacy: "

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF :ip v4 sock_stream: TCP
server.bind(ADDR)


def handleClient(connection, address):
    print(f"[Active Connection:] {address} connection")
    connection.send((PREFIX + "Welcome to our chatbot!").encode(FORMAT))
    connection.send((PREFIX + "How can we help you?").encode(FORMAT))

    connected = True
    while connected:
        try:
            connection.settimeout(20.0)  # timeouts 20 sec
            msg_length = connection.recv(HEADER).decode(
                FORMAT
            )  # wait untill sth is sent over the socket (we 'll determine how many bites we will accept)
            connection.settimeout(None)
            if msg_length:
                msg_length = int(msg_length)
                msg = connection.recv(msg_length).decode(FORMAT)  # the actual msg
                if msg == DISSCONECT_MSG:
                    print(f"[DISCONNECTED] {address} has disconnected")
                    connection.send("Thank you!".encode(FORMAT))
                    connected = False
                    continue
                print(f"[{address}] {msg}")
                connection.send((PREFIX + "Msg Received Porperly!").encode(FORMAT))
        except socket.timeout as e:
            print("[TIME OUT] Timed out after 20 seconds")
            connection.send("Connection Timed Out!".encode(FORMAT))
            print(f"[DISCONNECTED] {address} has disconnected")
            connected = False

    connection.close()


def start():  # it 'll start the socket server for us
    server.listen()
    print(f"[LISTENING] The Server Is Listening On: {SERVER}")
    while True:
        (
            connection,
            address,
        ) = (
            server.accept()
        )  # we 'll wait until a new connection occurs and save which address it came from and the acual object
        thread = threading.Thread(target=handleClient, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS: ]{threading.active_count() -1}")


print("[STARTING] the server is starting ...")
start()
