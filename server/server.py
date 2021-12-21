import socket
import threading
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", database="Pharmacy")
mycursor = mydb.cursor()

HEADER = 64
PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf_8"
DISSCONECT_MSG = "Close"
PREFIX = "Pharmacy: "

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def start():
    server.listen()
    print(f"[LISTENING] The Server Is Listening On: {SERVER}")
    while True:
        (
            connection,
            address,
        ) = server.accept()
        thread = threading.Thread(target=handleClient, args=(connection, address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS: ]{threading.active_count() -1}")


def handleClient(connection, address):
    print(f"[Active Connection:] {address} connection")
    sendMessage(connection, PREFIX + "Welcome to our chatbot!")

    sendMessage(connection, "How can we help you?")

    sendMessage(connection, "A specific product? Type (product)")

    sendMessage(connection, "A medicine for a specific condition? Type (condition)")

    connected = True
    while connected:
        try:
            session(connection)
        except socket.timeout as e:
            print("[TIME OUT] Timed out after 20 seconds")
            sendMessage(connection, "Connection Timed Out!")
            print(f"[DISCONNECTED] {address} has disconnected")
            connected = False

    connection.close()


def sendMessage(connection, message):
    message = message.encode(FORMAT)

    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b" " * (HEADER - len(send_len))

    connection.send(send_len)
    connection.send(message)


def session(connection):
    request = receiveMessage(connection)
    if request == "Product":
        categories = getCategories(connection)
        printData(connection, categories)
        status = purchaseProcess(connection)
        if status:
            finishTransaction(connection)
        else:
            sendMessage(connection, PREFIX + "We are sorry to see you go..")
    elif request == "Condition":
        diseases = getDiseases(connection)
        printData(connection, diseases)
        status = purchaseProcess(connection)
        if status:
            finishTransaction(connection)
        else:
            sendMessage(connection, PREFIX + "We are sorry to see you go..")
    else:
        sendMessage(connection, PREFIX + "You can type (product) or (condition) only!")


def receiveMessage(connection):
    connection.settimeout(20.0)
    msg_length = connection.recv(HEADER).decode(FORMAT)
    connection.settimeout(None)
    msg_length = int(msg_length)
    msg = connection.recv(msg_length).decode(FORMAT)

    return msg.title()


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


def printData(connection, data):
    for item in data:
        if item[0]=="":
            continue
        sendMessage(connection, item[0])


def purchaseProcess(connection):
    productName, productAmount = getProductData(connection)
    return confirmPurchase(connection, productName, productAmount)


def getProductData(connection):
    prices, amounts = getProductsData(connection)

    productName = getProductName(connection, prices)

    productPrice = prices[productName]
    productAmount = amounts[productName]

    sendMessage(
        connection,
        PREFIX
        + "Product's price is "
        + str(productPrice)
        + " LE. Would you like to buy it? (Yes/No)",
    )
    return productName, productAmount


def getProductsData(connection):
    products = []
    while len(products) == 0:
        type = receiveMessage(connection)
        mycursor.execute(
            "SELECT Name,Price,Amount FROM Medicines WHERE (Disease = %s OR Category = %s) AND Amount>0",
            (type, type),
        )
        products = mycursor.fetchall()
        if len(products) == 0:
            sendMessage(connection, PREFIX + "No results found!")
            sendMessage(connection, "Please select one of the items above")

    sendMessage(connection, PREFIX + "Please type the product name from the list below")

    prices = {}
    amounts = {}

    for item in products:
        sendMessage(connection, item[0])
        prices[item[0]] = item[1]
        amounts[item[0]] = item[2]

    return prices, amounts


def getProductName(connection, data):
    productName = receiveMessage(connection)
    while productName not in data.keys():
        sendMessage(connection, PREFIX + "No results found!")
        sendMessage(connection, "Please select one of the items above")
        productName = receiveMessage(connection)

    return productName


def confirmPurchase(connection, productName, productAmount):
    response = receiveMessage(connection)
    if response == "Yes":
        getAmount(connection, productName, productAmount)
        sendMessage(
            connection, PREFIX + "Would you like to have another order? (Yes/No)"
        )
        response = receiveMessage(connection)
        if response == "Yes":
            categories = getCategories(connection)
            printData(connection, categories)
            purchaseProcess(connection)
        return True
    elif response == "No":
        return False
    else:
        sendMessage(connection, PREFIX + "Please choose (Yes) or (No)")
        confirmPurchase(connection, productName, productAmount)


def getAmount(connection, productName, productAmount):
    sendMessage(connection, PREFIX + "How many?")

    amount = receiveMessage(connection)
    while not amount.isnumeric() or int(amount) <= 0:
        sendMessage(connection, PREFIX + "Please enter a valid amount!")
        amount = receiveMessage(connection)

    newAmount = productAmount - int(amount)
    if int(amount) > productAmount:
        sendMessage(
            connection, PREFIX + "Only " + str(productAmount) + " left in stock.."
        )
        newAmount = 0

    mycursor.execute(
        "UPDATE medicines SET Amount = %s WHERE Name = %s",
        (
            str(newAmount),
            productName,
        ),
    )
    mydb.commit()


def finishTransaction(connection):
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
    if not clientAddress:
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
