import socket
import threading
  # to create multiple threads with one python program

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

def buyProcess(connection):
    msg = receiveMessage(connection)
    
    sendMessage(connection, PREFIX + "Please type the product name from the list below")
    # Check database for products by symptom (msg)
    products = ['brufen','panadol','cataflam']
    for item in products:
        sendMessage(connection,item)
    
    msg = receiveMessage(connection)
    
    # Check database for product
    productPrice = 12
    productAmount = 2

    sendMessage(connection, PREFIX + "Product's price is "+str(productPrice)+" LE. Would you like to buy it?")

    msg = receiveMessage(connection)
    if msg=="yes":
        sendMessage(connection, PREFIX + "How many?")

        msg = receiveMessage(connection)

        sendMessage(connection, PREFIX + "Please type your phone number")

        msg = receiveMessage(connection)

        # If number not found in database
        sendMessage(connection, PREFIX + "Please type your address")

        msg = receiveMessage(connection)

        sendMessage(connection, PREFIX + "Thank you! Your order will arrive shortly!")

    elif msg=="no":
        sendMessage(connection, PREFIX + "We are sorry to see you go..")

def receiveMessage(connection):
    connection.settimeout(20.0)  # timeouts 20 sec
    msg_length = connection.recv(HEADER).decode(
        FORMAT
    )  # wait untill sth is sent over the socket (we 'll determine how many bites we will accept)
    connection.settimeout(None)
    msg_length = int(msg_length)
    msg = connection.recv(msg_length).decode(FORMAT)  # the actual msg

    return msg

def sendMessage(connection, message):
    message = message.encode(FORMAT)

    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b" " * (HEADER - len(send_len))

    connection.send(send_len)
    connection.send(message)

def handleClient(connection, address):
    print(f"[Active Connection:] {address} connection")
    sendMessage(connection, PREFIX + "Welcome to our chatbot!")

    sendMessage(connection, "How can we help you?")

    sendMessage(connection, "A specific product? Type (product)")

    sendMessage(connection, "A medicine for a specific condition? Type (condition)")

    connected = True
    while connected:
        try:
            msg = receiveMessage(connection)
            if msg == DISSCONECT_MSG:
                print(f"[DISCONNECTED] {address} has disconnected")
                sendMessage(connection, "Thank you!")
                connected = False
                continue
            if msg == 'product':
                sendMessage(connection, PREFIX + "Please type the category name from the list below")
                # Check database for categories
                categories = ['skin care','hair care','medicine']
                for item in categories:
                    sendMessage(connection,item)

                buyProcess(connection)

            if msg == 'condition':
                sendMessage(connection, PREFIX + "Please type the condition name from the list below")
                # Check database for conditions
                conditions = ['swelling','fever','coughing']
                for item in conditions:
                    sendMessage(connection, item)

                buyProcess(connection)
                
            print(f"[{address}] {msg}")
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
