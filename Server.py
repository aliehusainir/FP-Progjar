import socket
import threading


class User:
    def __init__(self, username, state, decklist):
        self.username = username
        self.state = state
        self.decklist = decklist


class Card:
    def __init__(self, cardtype):
        self.type = cardtype


def read_msg(clients, sock_cli, addr_cli, user, userlist):
    while True:
        data = sock_cli.recv(65535)
        if len(data) == 0:
            break
    sock_cli.close()
    print("Connection closed", addr_cli)
    userlist.remove(user)


def send_bcast(clients, data, sender_addr_cli):
    pass


def send_msg(sock_cli, data):
    pass


sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("0.0.0.0", 50000))
sock_server.listen(5)

clients = {}
userlist = []

while True:
    sock_cli, addr_cli = sock_server.accept()
    username_cli = sock_cli.recv(65535).decode("utf-8")
    print(username_cli, " joined")
    user = User(username_cli, "LOBBY", (0, 0, 0))
    userlist.append(user)

    thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, user, userlist))
    thread_cli.start()

    clients[user] = (sock_cli, addr_cli, thread_cli)
