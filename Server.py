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

        if user.state == "LOBBY":
            msg = data.decode("utf-8").split("|")
            if len(msg) == 1 and msg[0] == "Lihat deck":
                send_msg(sock_cli, "\nDeck saat ini:" +
                         "\nBatu: " + str(user.decklist[0]) +
                         "\nGunting: " + str(user.decklist[1]) +
                         "\nKertas: " + str(user.decklist[2]))
            elif len(msg) == 1 and msg[0] == "Buat deck":
                send_msg(sock_cli, "\nDeck saat ini:" +
                                   "\nBatu: " + str(user.decklist[0]) +
                                   "\nGunting: " + str(user.decklist[1]) +
                                   "\nKertas: " + str(user.decklist[2]))
                user.state = "DECKBUILDING"
        elif user.state == "DECKBUILDING":
            msg = data.decode("utf-8").split()
            user.decklist = (int(msg[0]), int(msg[1]), int(msg[2]))
            user.state = "LOBBY"
    sock_cli.close()
    print("Connection closed", addr_cli)
    userlist.remove(user)


def send_bcast(clients, data, sender_addr_cli):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data)


def send_msg(sock_cli, data):
    sock_cli.send(bytes(data, "utf-8"))


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
