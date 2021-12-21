from socket import AF_INET, socket, SOCK_STREAM, timeout
import threading
import mysql.connector
import time


# Connecting to database server
mydb = mysql.connector.connect(host="localhost", user="root", database="pharmacy")
mycursor = mydb.cursor()

BUFFERSIZE = 64
PORT = 5050
SERVER = "localhost"
FORMAT = "utf_8"

# AF :IPv4
# SOCK_STREAM: TCP
server = socket(AF_INET, SOCK_STREAM)

# Assign IP address and port to the socket
server.bind((SERVER, PORT))

# Start listening to requests
def start():
    server.listen()
    print(f"[LISTENING] The Server Is Listening On: {SERVER}")
    while True:
        # Save the socket's object connecting to the server
        connection, _ = server.accept()

        # Handle the client request on a new thread to avoid blocking new requests
        thread = threading.Thread(target=handleClient, args=(connection,))
        thread.start()
        print(f"[ACTIVE CONNECTIONS: ]{threading.active_count() -1}")


def handleClient(connection):
    global PREFIX

    PREFIX = "Pharmacy: "

    sendMessage(connection, PREFIX + "Welcome to our chatbot!")
    sendMessage(connection, "How can we help you?")
    sendMessage(connection, "A specific product? Type (product)")
    sendMessage(connection, "A medicine for a specific condition? Type (condition)")

    # Stay connected until the connection times out
    connected = True
    while connected:
        try:
            session(connection)
        except timeout:
            print("[TIME OUT] Timed out after 20 seconds")
            sendMessage(connection, "Time Out! Type (restart) if you want to reconnect")
            try:
                request = receiveMessage(connection)
                if request == "Restart":
                    handleClient(connection)
                else:
                    raise Exception("Invalid input")
            except:
                time.sleep(10)
                sendMessage(connection, "Connection Timed Out!")
                print(f"[DISCONNECTED] Client has disconnected")
                connected = False

    connection.close()


def sendMessage(connection, message):
    message = message.encode(FORMAT)

    # Calculate and send message length in bytes to avoid sending excess data
    messageLength = str(len(message)).encode(FORMAT)
    messageLength += b" " * (BUFFERSIZE - len(messageLength))

    connection.send(messageLength)
    connection.send(message)


def session(connection):
    request = receiveMessage(connection)
    if request == "Product":
        categories = getCategories(connection)
        sendData(connection, categories)
        purchase(connection)
    elif request == "Condition":
        diseases = getDiseases(connection)
        sendData(connection, diseases)
        purchase(connection)
    else:
        sendMessage(connection, PREFIX + "You can type (product) or (condition) only!")


def receiveMessage(connection):
    # Client sends the message length in bytes to avoid receiving excess data
    connection.settimeout(20.0)
    messageLength = connection.recv(BUFFERSIZE).decode(FORMAT)
    connection.settimeout(None)

    messageLength = int(messageLength)
    message = connection.recv(messageLength).decode(FORMAT)

    # Use title method to unify strings case
    return message.title()


def getCategories(connection):
    sendMessage(
        connection, PREFIX + "Please type the category name from the list below"
    )
    mycursor.execute("SELECT Category FROM Medicines GROUP BY Category")
    return mycursor.fetchall()


def getDiseases(connection):
    sendMessage(
        connection, PREFIX + "Please type the condition name from the list below"
    )
    mycursor.execute("SELECT Disease FROM Medicines GROUP BY Disease")
    return mycursor.fetchall()


def sendData(connection, tableData):
    # Each row is a list of columns (Category or Disease)
    for row in tableData:
        if row[0] == "":
            continue
        sendMessage(connection, row[0])


def purchase(connection):
    # Complete the process if the client chose to buy a product
    status = chooseProduct(connection)
    if status:
        getClientInfo(connection)
    else:
        sendMessage(connection, PREFIX + "We are sorry to see you go..")


def chooseProduct(connection):
    productName, productQuantity = getProductData(connection)
    return confirmPurchase(connection, productName, productQuantity)


def getProductData(connection):
    prices, amounts = getProductsData(connection)

    # Send prices dictionary as a parameter to check
    # whether we have the product that the user selected.
    productName = getProductName(connection, prices)

    productPrice = prices[productName]
    productQuantity = amounts[productName]

    sendMessage(
        connection,
        PREFIX
        + "Product's price is "
        + str(productPrice)
        + " LE. Would you like to buy it? (Yes/No)",
    )
    return productName, productQuantity


def getProductsData(connection):
    productsTableData = []
    while len(productsTableData) == 0:
        productType = receiveMessage(connection)
        mycursor.execute(
            "SELECT Name,Price,Amount FROM Medicines WHERE (Disease = %s OR Category = %s) AND Amount>0",
            (productType, productType),
        )
        productsTableData = mycursor.fetchall()
        if len(productsTableData) == 0:
            sendMessage(connection, PREFIX + "No results found!")
            sendMessage(connection, "Please select one of the items above")

    sendMessage(connection, PREFIX + "Please type the product name from the list below")

    prices = {}
    amounts = {}
    # Each row is a list of columns (Name, Price, Amount)
    # Use table data to fill prices and amounts dictionaries
    # (key, value) = product's name, product's price or quantity
    for row in productsTableData:
        sendMessage(connection, row[0])
        prices[row[0]] = row[1]
        amounts[row[0]] = row[2]

    return prices, amounts


def getProductName(connection, data):
    productName = receiveMessage(connection)
    while productName not in data.keys():
        sendMessage(connection, PREFIX + "No results found!")
        sendMessage(connection, "Please select one of the items above")
        productName = receiveMessage(connection)

    return productName


def confirmPurchase(connection, productName, productQuantity):
    response = receiveMessage(connection)
    if response == "Yes":
        getQuantity(connection, productName, productQuantity)
        sendMessage(
            connection, PREFIX + "Would you like to have another order? (Yes/No)"
        )
        response = receiveMessage(connection)
        if response == "Yes":
            categories = getCategories(connection)
            sendData(connection, categories)
            chooseProduct(connection)
        return True
    elif response == "No":
        return False
    else:
        sendMessage(connection, PREFIX + "Please choose (Yes) or (No)")
        confirmPurchase(connection, productName, productQuantity)


def getQuantity(connection, productName, productQuantity):
    sendMessage(connection, PREFIX + "How many?")

    requiredQuantity = receiveMessage(connection)

    # Check if input is an integer bigger than zero
    while not requiredQuantity.isnumeric() or int(requiredQuantity) <= 0:
        sendMessage(connection, PREFIX + "Please enter a valid requiredQuantity!")
        requiredQuantity = receiveMessage(connection)

    # Check if required quantity is available in stock
    newQuantity = productQuantity - int(requiredQuantity)
    if newQuantity < 0:
        sendMessage(
            connection, PREFIX + "Only " + str(productQuantity) + " left in stock.."
        )
        newQuantity = 0

    mycursor.execute(
        "UPDATE medicines SET Amount = %s WHERE Name = %s",
        (
            str(newQuantity),
            productName,
        ),
    )
    mydb.commit()


def getClientInfo(connection):
    clientPhoneNumber = getPhoneNumber(connection)
    handleAddress(connection, clientPhoneNumber)
    sendMessage(connection, PREFIX + "Thank you! Your order will arrive shortly!")


def getPhoneNumber(connection):
    sendMessage(connection, PREFIX + "Please type your phone number")

    clientPhoneNumber = receiveMessage(connection)
    while not clientPhoneNumber.isnumeric():
        sendMessage(connection, PREFIX + "Please enter a valid phone number!")
        clientPhoneNumber = receiveMessage(connection)

    return clientPhoneNumber


def handleAddress(connection, clientPhoneNumber):
    mycursor.execute(
        "SELECT address FROM clients WHERE phoneNumber = %s", (clientPhoneNumber,)
    )
    clientAddress = mycursor.fetchone()
    if clientAddress is None:
        insertAddress(connection, clientPhoneNumber)
    else:
        sendMessage(connection, PREFIX + "Your address is: " + clientAddress[0])
        sendMessage(connection, "Would you like to update your address? (Yes/No)")
        updateAddress(connection, clientPhoneNumber)


def insertAddress(connection, clientPhoneNumber):
    sendMessage(connection, PREFIX + "Please type your address")
    clientAddress = receiveMessage(connection)
    mycursor.execute(
        "INSERT INTO clients (phoneNumber,address) VALUES (%s,%s)",
        (clientPhoneNumber, clientAddress),
    )
    mydb.commit()


def updateAddress(connection, clientPhoneNumber):
    response = receiveMessage(connection)

    if response == "Yes":
        sendMessage(connection, PREFIX + "Please type your address")
        clientAddress = receiveMessage(connection)
        mycursor.execute(
            "UPDATE clients SET address = %s WHERE phoneNumber = %s",
            (
                clientAddress,
                clientPhoneNumber,
            ),
        )
        mydb.commit()
    elif response == "No":
        return
    else:
        sendMessage(connection, PREFIX + "Please choose (Yes) or (No)")
        updateAddress(connection, clientPhoneNumber)


print("[STARTING] the server is starting ...")
start()
