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
            if len(msg) == 1:
                if msg[0] == "Lihat deck":
                    send_msg(sock_cli, "\nDeck saat ini:" +
                             "\nBatu: " + str(user.decklist[0]) +
                             "\nGunting: " + str(user.decklist[1]) +
                             "\nKertas: " + str(user.decklist[2]), msg[0])
                elif msg[0] == "Buat deck":
                    send_msg(sock_cli, "\nDeck saat ini:" +
                                       "\nBatu: " + str(user.decklist[0]) +
                                       "\nGunting: " + str(user.decklist[1]) +
                                       "\nKertas: " + str(user.decklist[2]), msg[0])
                    user.state = "DECKBUILDING"
                elif msg[0] == "Buat room":
                    user.state = "ROOM"
                elif msg[0] == "Terima undangan":
                    menu = "\nPilih pemain:\n"
                    for u in invitationlist[user]:
                        menu = menu + u + "\n"
                    menu = menu + "Kembali ke lobi\n"
                    send_msg(sock_cli, menu, "Terima")
                    user.state = "ACCEPTING"

            elif msg[0] == "bcast":
                sendmsg = "<{}>: {}".format(user.username, msg[1])
                send_bcast(clients, sendmsg, addr_cli, msg[0])

            elif msg[0] == "add":
                for u in userlist:
                    #if msg[1] == u.username:
                        #send_msg(sock_cli, msg[1] + " tidak ditemukan", msg[0])
                    if msg[1] in friendlist[user]:
                        send_msg(sock_cli, "Sudah berteman dengan " + msg[1], msg[0])
                        break
                    elif msg[1] == u.username:
                        friendlist[user].append(u.username)
                        friendlist[u].append(user.username)
                        send_msg(sock_cli, msg[1] + " berhasil ditambahkan", msg[0])
                        send_msg(clients[u][0], user.username + " telah menambahkanmu", msg[0])
                        break
                        
            elif msg[0] == "chat":
                sendmsg = "<{}>: {}".format(user.username, msg[2])
                for u in userlist:
                    if msg[1] in friendlist[user]:
                        if msg[1] == u.username:
                            send_msg(clients[u][0], sendmsg, msg[0])
                            break
                    else:
                        send_msg(sock_cli, "User belum menjadi temanmu", msg[0])
                        break

        elif user.state == "DECKBUILDING":
            msg = data.decode("utf-8").split()
            user.decklist = (int(msg[0]), int(msg[1]), int(msg[2]))
            user.state = "LOBBY"
        elif user.state == "ROOM":
            msg = data.decode()
            if msg == "Lihat deck":
                send_msg(sock_cli, "\nDeck saat ini:" +
                         "\nBatu: " + str(user.decklist[0]) +
                         "\nGunting: " + str(user.decklist[1]) +
                         "\nKertas: " + str(user.decklist[2]), msg)
            elif msg.startswith("Undang "):
                msg = msg.replace("Undang ", '')
                print(msg)
                if msg == user.username:
                    send_msg(sock_cli, "Tidak bisa mengundang diri sendiri", "Undang")
                    continue
                for u in userlist:
                    if msg == u.username:
                        send_msg(sock_cli, msg + " berhasil diundang", "Undang")
                        invitationlist[u].append(user.username)
                        break
                else:
                    send_msg(sock_cli, "Username tidak ditemukan", "Undang")
            elif msg == "Kembali ke lobi":
                for l in invitationlist.values():
                    if user.username in l:
                        remove(user.username)
                user.state = "LOBBY"
        elif user.state == "ACCEPTING":
            msg = data.decode()
            if msg == "Kembali ke lobi":
                user.state = "LOBBY"
            else:
                for u in userlist:
                    if msg == u.username:
                        send_msg(sock_cli, "\nPermainan berhasil diterima", "Terima")
                        user.state = "ROOM"
                        break
                else:
                    send_msg(sock_cli, "\nUsername tidak ditemukan", "Terima")
                    menu = "\nPilih pemain:\n"
                    for u in invitationlist[user]:
                        menu = menu + u + "\n"
                    menu = menu + "Kembali ke lobi"
                    send_msg(sock_cli, menu, "Pilih")
        print(data)
    sock_cli.close()
    print("Connection closed", addr_cli)
    userlist.remove(user)
    for username in friendlist:
        if user in friendlist[username]:
            friendlist[username].remove(user)


def send_bcast(clients, data, sender_addr_cli, option):
    for sock_cli, addr_cli, _ in clients.values():
        if not (sender_addr_cli[0] and sender_addr_cli[1] == addr_cli[1]):
            send_msg(sock_cli, data, option)

def send_msg(sock_cli, data, option):
    sock_cli.send(bytes("{}|{}".format(data, option), "utf-8"))


sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("0.0.0.0", 50000))
sock_server.listen(5)

clients = {}
userlist = []
invitationlist = {}
friendlist = {}


while True:
    sock_cli, addr_cli = sock_server.accept()
    username_cli = sock_cli.recv(65535).decode("utf-8")
    print(username_cli, "joined")
    user = User(username_cli, "LOBBY", (0, 0, 0))
    userlist.append(user)

    thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, user, userlist))
    thread_cli.start()

    clients[user] = (sock_cli, addr_cli, thread_cli)
    invitationlist[user] = []
    friendlist[user] = []

