import socket
import threading


class User:
    def __init__(self, username, state, decklist):
        self.username = username
        self.state = state
        self.decklist = decklist


class Card:
    def __init__(self, cardtype):
        self.cardtype = cardtype

    def get_cardtype(self):
        return self.cardtype

    def set_cardtype(self, newtype):
        self.cardtype = newtype


class Game:
    def __init__(self, p1hand, p2hand, p1deck, p2deck):
        self.p1ready = False
        self.p2ready = False
        self.p1hand = p1hand
        self.p2hand = p2hand
        self.p1deck = p1deck
        self.p2deck = p2deck
        self.p1played = None
        self.p2played = None
        self.p1score = 0
        self.p2score = 0

    def is_ready(self):
        if self.p1ready and self.p2ready:
            return True
        else:
            return False

    def set_unready(self):
        self.p1ready = False
        self.p2ready = False

    def set_ready(self, player):
        if player == "p1":
            self.p1ready = True
        elif player == "p2":
            self.p2ready = True

    def get_hand(self, player):
        if player == "p1":
            return self.p1hand
        elif player == "p2":
            return self.p2hand

    def draw(self, player):
        if player == "p1":
            if self.p1deck:
                self.p1hand.append(self.p1deck.pop())
        elif player == "p2":
            if self.p1deck:
                self.p2hand.append(self.p2deck.pop())

    def draw_n(self, player, amount):
        for n in range(amount):
            draw(self, player)

    def discard(self, player, indices):
        discarded = []
        if player == "p1":
            for i in indices:
                discarded.append(self.p1hand.pop(i))
        elif player == "p2":
            for i in indices:
                discarded.append(self.p2hand.pop(i))
        return discarded

    def add_wildcard(self, player):
        if player == "p1":
            self.p1hand.append(Card("Wildcard"))

    def play(self, player, index):
        if player == "p1":
            if index is None:
                self.p1played = None
            else:
                self.p1played = self.p1hand.pop(index)
                return self.p1played.get_cardtype()
        elif player == "p2":
            if index is None:
                self.p2played = None
            else:
                self.p2played = self.p2hand.pop(index)
                return self.p2played.get_cardtype()

    def showdown(self):
        if self.p1played is None and self.p2played is None:
            return None
        elif self.p1played is None:
            return "p2"
        elif self.p2played is None:
            return "p1"
        else:
            if self.p1played.get_cardtype() == self.p2played.get_cardtype():
                return None
            elif self.p1played.get_cardtype() == "Rock" and self.p2played.get_cardtype() == "Paper":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Paper" and self.p2played.get_cardtype() == "Scissors":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Scissors" and self.p2played.get_cardtype() == "Rock":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Rock" and self.p2played.get_cardtype() == "Scissors":
                self.p1score += 1
                return "p1"
            elif self.p1played.get_cardtype() == "Scissors" and self.p2played.get_cardtype() == "Paper":
                self.p1score += 1
                return "p1"
            elif self.p1played.get_cardtype() == "Paper" and self.p2played.get_cardtype() == "Rock":
                self.p1score += 1
                return "p1"


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
                    roomlist.append([user])
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
                msg = msg.replace("Undang ", "")
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
                for li in invitationlist.values():
                    if user.username in li:
                        li.remove(user.username)
                for room in roomlist.values:
                    if room[0] == user:
                        roomlist.remove(room)
                    elif room[1] == user:
                        room.pop(1)
                        send_msg(clients[room[0]][0], user.username + " telah meninggalkan room", "GUEST_LEAVES")
                user.state = "LOBBY"
        elif user.state == "ACCEPTING":
            msg = data.decode()
            if msg == "Kembali ke lobi":
                user.state = "LOBBY"
            else:
                found = False
                for u in userlist:
                    if msg == u.username:
                        found = True
                        for room in roomlist:
                            if room[0] == u:
                                if len(room) > 1:
                                    menu = "\nUser sudah memiliki lawan\nPilih pemain:\n"
                                    for i in invitationlist[user]:
                                        menu = menu + i + "\n"
                                    menu = menu + "Kembali ke lobi"
                                    send_msg(sock_cli, menu, "Pilih")
                                    break
                                room.append(user)
                                send_msg(sock_cli, "\nPermainan berhasil diterima", "TO_ROOM")
                                send_msg(clients[u][0], "\n" + user.username + " telah memasuki room", "GUEST_ENTERS")
                                for li in invitationlist.values():
                                    if u.username in li:
                                        li.remove(u.username)
                                user.state = "ROOM"
                                break
                    if found:
                        break
                else:
                    menu = "\nUsername tidak ditemukan\nPilih pemain:\n"
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
roomlist = []

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
