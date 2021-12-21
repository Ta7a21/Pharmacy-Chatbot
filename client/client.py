from socket import AF_INET,socket, SOCK_STREAM
from threading import Thread
import tkinter


def receive():
    while True:
        try:
            msg_length = client_socket.recv(HEADER).decode(
                FORMAT
            )
            client_socket.settimeout(None)
            if msg_length:
                msg_length = int(msg_length)
                msg = client_socket.recv(msg_length).decode(FORMAT)
            
                msg_list.insert(tkinter.END, msg)
                msg_list.yview(tkinter.END) 
                if msg == "Connection Timed Out!":
                    client_socket.close()
                    top.quit()
        except OSError:
            break


def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    message = msg.encode(FORMAT)

    msg_len = len(message)
    send_len = str(msg_len).encode(FORMAT)
    send_len += b" " * (HEADER - len(send_len))

    client_socket.send(send_len)
    client_socket.send(message)

    msg_list.insert(tkinter.END, PREFIX + msg)
    msg_list.yview(tkinter.END) 


def on_closing(event=None):
    client_socket.close()
    top.quit()


top = tkinter.Tk()
top.title("Pharmacy Chatbot")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)

msg_list = tkinter.Listbox(
    messages_frame, height=15, width=100, yscrollcommand=scrollbar.set
)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

HOST = 'localhost'
PORT = 5050
HEADER = 64
PREFIX = "You: "
FORMAT = "utf_8"
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()