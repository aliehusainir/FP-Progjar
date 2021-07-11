import socket
import threading
import random
import time


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
        self.state = "MULLIGAN"
        self.round = 1

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

    def get_state(self):
        return self.state

    def set_state(self, newstate):
        self.state = newstate

    def get_hand(self, player):
        if player == "p1":
            return self.p1hand
        elif player == "p2":
            return self.p2hand

    def shuffle_deck(self, player):
        if player == "p1":
            random.shuffle(self.p1deck)
        elif player == "p2":
            random.shuffle(self.p2deck)

    def draw(self, player):
        drawn = None
        if player == "p1":
            if self.p1deck:
                drawn = self.p1deck.pop()
                self.p1hand.append(drawn)
        elif player == "p2":
            if self.p1deck:
                drawn = self.p2deck.pop()
                self.p2hand.append(drawn)
        return drawn

    def draw_n(self, player, amount):
        for n in range(amount):
            self.draw(player)

    def mulligan(self, player, indices):
        if player == "p1":
            for i in indices:
                self.p1deck.append(self.p1hand.pop(i-1))
        elif player == "p2":
            for i in indices:
                self.p2deck.append(self.p2hand.pop(i-1))
        self.shuffle_deck(player)
        self.draw_n(player, len(indices))

    def discard(self, player, indices):
        discarded = []
        if player == "p1":
            for i in indices:
                discarded.append(self.p1hand.pop(i-1))
        elif player == "p2":
            for i in indices:
                discarded.append(self.p2hand.pop(i-1))
        return discarded

    def add_wildcard(self, player):
        if player == "p1":
            self.p1hand.append(Card("Wildcard"))
        elif player == "p2":
            self.p2hand.append(Card("Wildcard"))

    def get_played(self, player):
        if player == "p1":
            if self.p1played is None:
                return None
            else:
                return self.p1played.get_cardtype()
        elif player == "p2":
            if self.p2played is None:
                return None
            else:
                return self.p2played.get_cardtype()

    def set_played(self, player, index):
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
            elif self.p1played.get_cardtype() == "Batu" and self.p2played.get_cardtype() == "Kertas":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Kertas" and self.p2played.get_cardtype() == "Gunting":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Gunting" and self.p2played.get_cardtype() == "Batu":
                self.p2score += 1
                return "p2"
            elif self.p1played.get_cardtype() == "Batu" and self.p2played.get_cardtype() == "Gunting":
                self.p1score += 1
                return "p1"
            elif self.p1played.get_cardtype() == "Gunting" and self.p2played.get_cardtype() == "Kertas":
                self.p1score += 1
                return "p1"
            elif self.p1played.get_cardtype() == "Kertas" and self.p2played.get_cardtype() == "Batu":
                self.p1score += 1
                return "p1"

    def get_score(self, player):
        if player == "p1":
            return self.p1score
        elif player == "p2":
            return self.p2score

    def get_round(self):
        return self.round

    def advance_round(self):
        self.round += 1


def create_deck(player):
    deck = []
    for x in range(int(player.decklist[0])):
        deck.append(Card("Batu"))
    for x in range(int(player.decklist[1])):
        deck.append(Card("Gunting"))
    for x in range(int(player.decklist[2])):
        deck.append(Card("Kertas"))
    random.shuffle(deck)
    return deck


def create_hand(deck):
    hand = []
    for n in range(5):
        hand.append(deck.pop())
    return hand


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
            elif msg == "Mulai permainan" or msg == "Siap bermain":
                user.state = "READY"
                for room in roomlist:
                    if user in room:
                        p1 = room[0]
                        p2 = room[1]
                        if p1.state == p2.state:
                            p1deck = create_deck(p1)
                            p2deck = create_deck(p2)
                            p1hand = create_hand(p1deck)
                            p2hand = create_hand(p2deck)
                            room.append(Game(p1hand, p2hand, p1deck, p2deck))
                            p1msg = "\nPermainan dimulai\nFase mulligan\nHand anda:\n"
                            p2msg = "\nPermainan dimulai\nFase mulligan\nHand anda:\n"
                            for x in range(5):
                                p1msg = p1msg + str(x+1) + ". " + p1hand[x].get_cardtype() + "\n"
                                p2msg = p2msg + str(x+1) + ". " + p2hand[x].get_cardtype() + "\n"
                                if x == 4:
                                    p1msg = p1msg + "Pilih kartu yang ingin anda kembalikan (tekan enter untuk skip)"
                                    p2msg = p2msg + "Pilih kartu yang ingin anda kembalikan (tekan enter untuk skip)"
                            send_msg(clients[p1][0], p1msg, "TO_GAME")
                            send_msg(clients[p2][0], p2msg, "TO_GAME")
                            p1.state = "GAME"
                            p2.state = "GAME"
                            break
            elif msg == "Kembali ke lobi":
                for li in invitationlist.values():
                    if user.username in li:
                        li.remove(user.username)
                for room in roomlist:
                    if room[0] == user:
                        if len(room) > 1:
                            send_msg(clients[room[1]][0], "Room dibubarkan oleh host", "TO_LOBBY")
                            room[1].state = "LOBBY"
                        roomlist.remove(room)
                    elif len(room) > 1 and room[1] == user:
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
        elif user.state == "READY":
            msg = data.decode()
            if msg == "Batalkan":
                user.state = "ROOM"
        elif user.state == "GAME":
            msg = data.decode().split()
            if msg:
                msg = list(map(int, msg))
                msg.sort(reverse=True)
            for room in roomlist:
                if user in room:
                    game = room[2]
                    gamestate = game.get_state()
                    player = None
                    if user == room[0]:
                        player = "p1"
                    elif user == room[1]:
                        player = "p2"
                    hand = game.get_hand(player)
                    if msg:
                        invalidmsg = False
                        for n in msg:
                            if n > len(hand):
                                send_msg(sock_cli, "\nJumlah kartu di tangan hanya " + str(len(hand)) + "\n", "Invalid")
                                invalidmsg = True
                                break
                        if invalidmsg:
                            break
                    if gamestate == "MULLIGAN":
                        if msg:
                            game.mulligan(player, msg)
                        msg = "\nHand anda menjadi:\n"
                        for x in range(len(hand)):
                            msg = msg + str(x+1) + ". " + hand[x].get_cardtype() + "\n"
                        send_msg(sock_cli, msg, "INPUT_RECEIVED")
                        game.set_ready(player)
                        if game.is_ready():
                            time.sleep(0.5)
                            p1 = room[0]
                            p2 = room[1]
                            p1hand = game.get_hand("p1")
                            p2hand = game.get_hand("p2")
                            gameround = game.get_round()
                            p1draw = game.draw("p1")
                            if p1draw is None:
                                p1draw = Card("None")
                            p2draw = game.draw("p2")
                            if p2draw is None:
                                p2draw = Card("None")
                            p1msg = ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                     p1draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                            p2msg = ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                     p2draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                            for x in range(len(p1hand)):
                                p1msg = p1msg + str(x + 1) + ". " + p1hand[x].get_cardtype() + "\n"
                            for x in range(len(p2hand)):
                                p2msg = p2msg + str(x + 1) + ". " + p2hand[x].get_cardtype() + "\n"
                            send_msg(clients[p1][0], p1msg, "INPUT_RESET")
                            send_msg(clients[p2][0], p2msg, "INPUT_RESET")
                            game.set_state("WILDCARD")
                            game.set_unready()
                            break
                        else:
                            break
                    elif gamestate == "WILDCARD":
                        if len(msg) == 2:
                            if hand[msg[0]-1].get_cardtype() == hand[msg[1]-1].get_cardtype():
                                discarded = game.discard(player, msg)
                                game.add_wildcard(player)
                                send_msg(sock_cli, "\nAnda membuang 2 " + discarded[0].get_cardtype() +
                                         " dan mendapatkan 1 wildcard\n", "INPUT_RECEIVED")
                                game.set_ready(player)
                            else:
                                send_msg(sock_cli, "\nBuang 2 kartu regular yang sama atau 1 wildcard\n", "Invalid")
                        elif len(msg) == 1:
                            if hand[msg[0]-1].get_cardtype() == "Wildcard":
                                discarded = game.discard(player, msg)
                                game.draw_n(player, 2)
                                send_msg(sock_cli, "\nAnda membuang 1 " + discarded[0].get_cardtype() +
                                         " dan mengambil 2 kartu dari deck\n", "INPUT_RECEIVED")
                                game.set_ready(player)
                            else:
                                send_msg(sock_cli, "\nBuang 2 kartu regular yang sama atau 1 wildcard\n", "Invalid")
                        elif len(msg) > 2:
                            send_msg(sock_cli, "\nBuang 2 kartu regular yang sama atau 1 wildcard\n", "Invalid")
                        else:
                            send_msg(sock_cli, "\nAnda tidak melakukan apa-apa pada fase wildcard\n", "INPUT_RECEIVED")
                            game.set_ready(player)
                        if game.is_ready():
                            time.sleep(0.5)
                            p1 = room[0]
                            p2 = room[1]
                            p1hand = game.get_hand("p1")
                            p2hand = game.get_hand("p2")
                            p1msg = "\nFase play\nHand anda:\n"
                            p2msg = "\nFase play\nHand anda:\n"
                            for x in range(len(p1hand)):
                                p1msg = p1msg + str(x + 1) + ". " + p1hand[x].get_cardtype() + "\n"
                            for x in range(len(p2hand)):
                                p2msg = p2msg + str(x + 1) + ". " + p2hand[x].get_cardtype() + "\n"
                            send_msg(clients[p1][0], p1msg, "INPUT_RESET")
                            send_msg(clients[p2][0], p2msg, "INPUT_RESET")
                            game.set_state("PLAY")
                            game.set_unready()
                            break
                        else:
                            break
                    elif gamestate == "PLAY":
                        if not msg:
                            if not hand:
                                game.set_played(player, None)
                                send_msg(sock_cli, "\nAnda tidak memainkan kartu apapun\n", "INPUT_RECEIVED")
                                game.set_ready(player)
                            else:
                                send_msg(sock_cli, "\nPilih sebuah kartu untuk dimainkan\n", "Invalid")
                        elif len(msg) == 1:
                            if hand[msg[0]-1].get_cardtype() == "Wildcard":
                                send_msg(sock_cli, "\nMainkan wildcard sebagai:\n"
                                                   "1. Batu\n"
                                                   "2. Gunting\n"
                                                   "3. Kertas\n", "Wildcard")
                                user.state = "CHOOSING"
                            else:
                                played = game.set_played(player, msg[0]-1)
                                send_msg(sock_cli, "\nAnda memainkan " + played + "\n", "INPUT_RECEIVED")
                                game.set_ready(player)
                                if game.is_ready():
                                    time.sleep(0.5)
                                    p1 = room[0]
                                    p2 = room[1]
                                    p1hand = game.get_hand("p1")
                                    p2hand = game.get_hand("p2")
                                    p1played = game.get_played("p1")
                                    p2played = game.get_played("p2")
                                    res = game.showdown()
                                    p1score = game.get_score("p1")
                                    p2score = game.get_score("p2")
                                    game.advance_round()
                                    gameround = game.get_round()
                                    p1msg = "\nMusuh mengeluarkan " + p2played
                                    p2msg = "\nMusuh mengeluarkan " + p1played
                                    if res is None:
                                        p1msg = p1msg + "\nRonde seri, skor tetap " + str(p1score) + "-" + str(p2score)
                                        p2msg = p2msg + "\nRonde seri, skor tetap " + str(p1score) + "-" + str(p2score)
                                    elif res == "p1":
                                        p1msg = p1msg + "\nAnda menang, skor menjadi " + str(p1score) + "-" + str(
                                            p2score)
                                        p2msg = p2msg + "\nAnda kalah, skor menjadi " + str(p1score) + "-" + str(
                                            p2score)
                                    elif res == "p2":
                                        p1msg = p1msg + "\nAnda kalah, skor menjadi " + str(p1score) + "-" + str(
                                            p2score)
                                        p2msg = p2msg + "\nAnda menang, skor menjadi " + str(p1score) + "-" + str(
                                            p2score)
                                    if p1score == 7:
                                        p1msg = p1msg + "\nPermainan dimenangkan oleh anda"
                                        p2msg = p2msg + "\nPermainan dimenangkan oleh musuh"
                                        send_msg(clients[p1][0], p1msg, "GAME_FINISHED")
                                        send_msg(clients[p2][0], p2msg, "GAME_FINISHED")
                                        p1.state = "ROOM"
                                        p2.state = "ROOM"
                                        room.pop()
                                        break
                                    elif p2score == 7:
                                        p1msg = p1msg + "\nPermainan dimenangkan oleh musuh"
                                        p2msg = p2msg + "\nPermainan dimenangkan oleh anda"
                                        send_msg(clients[p1][0], p1msg, "GAME_FINISHED")
                                        send_msg(clients[p2][0], p2msg, "GAME_FINISHED")
                                        p1.state = "ROOM"
                                        p2.state = "ROOM"
                                        room.pop()
                                        break
                                    p1draw = game.draw("p1")
                                    if p1draw is None:
                                        p1draw = Card("None")
                                    p2draw = game.draw("p2")
                                    if p2draw is None:
                                        p2draw = Card("None")
                                    p1msg = p1msg + ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                                     p1draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                                    p2msg = p2msg + ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                                     p2draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                                    for x in range(len(p1hand)):
                                        p1msg = p1msg + str(x + 1) + ". " + p1hand[x].get_cardtype() + "\n"
                                    for x in range(len(p2hand)):
                                        p2msg = p2msg + str(x + 1) + ". " + p2hand[x].get_cardtype() + "\n"
                                    send_msg(clients[p1][0], p1msg, "INPUT_RESET")
                                    send_msg(clients[p2][0], p2msg, "INPUT_RESET")
                                    game.set_state("WILDCARD")
                                    user.state = "GAME"
                                    game.set_unready()
                                    break
                        else:
                            send_msg(sock_cli, "\nPilih sebuah kartu untuk dimainkan\n", "Invalid")
        elif user.state == "CHOOSING":
            msg = data.decode().split()
            if not msg:
                send_msg(sock_cli, "\nMainkan wildcard sebagai:\n"
                                   "1. Batu\n"
                                   "2. Gunting\n"
                                   "3. Kertas\n", "Wildcard")
                continue
            msg = list(map(int, msg))
            msg.sort(reverse=True)
            for room in roomlist:
                if user in room:
                    game = room[2]
                    player = None
                    if user == room[0]:
                        player = "p1"
                    elif user == room[1]:
                        player = "p2"
                    hand = game.get_hand(player)
                    if len(msg) == 1 and msg[0] < 4:
                        index = None
                        cardtype = None
                        for x in range(len(hand)):
                            print(x)
                            if hand[x].get_cardtype() == "Wildcard":
                                if msg[0] == 1:
                                    cardtype = "Batu"
                                    hand[x].set_cardtype("Batu")
                                elif msg[0] == 2:
                                    cardtype = "Gunting"
                                    hand[x].set_cardtype("Gunting")
                                else:
                                    cardtype = "Kertas"
                                    hand[x].set_cardtype("Kertas")
                                index = x
                                break
                        game.set_played(player, index)
                        send_msg(sock_cli, "\nAnda memainkan wildcard sebagai " + cardtype + "\n", "INPUT_RECEIVED")
                        game.set_ready(player)
                        if game.is_ready():
                            time.sleep(0.5)
                            p1 = room[0]
                            p2 = room[1]
                            p1hand = game.get_hand("p1")
                            p2hand = game.get_hand("p2")
                            p1played = game.get_played("p1")
                            p2played = game.get_played("p2")
                            res = game.showdown()
                            p1score = game.get_score("p1")
                            p2score = game.get_score("p2")
                            game.advance_round()
                            gameround = game.get_round()
                            p1msg = "\nMusuh mengeluarkan " + p2played
                            p2msg = "\nMusuh mengeluarkan " + p1played
                            if res is None:
                                p1msg = p1msg + "\nRonde seri, skor tetap " + str(p1score) + "-" + str(p2score)
                                p2msg = p2msg + "\nRonde seri, skor tetap " + str(p1score) + "-" + str(p2score)
                            elif res == "p1":
                                p1msg = p1msg + "\nAnda menang, skor menjadi " + str(p1score) + "-" + str(p2score)
                                p2msg = p2msg + "\nAnda kalah, skor menjadi " + str(p1score) + "-" + str(p2score)
                            elif res == "p2":
                                p1msg = p1msg + "\nAnda kalah, skor menjadi " + str(p1score) + "-" + str(p2score)
                                p2msg = p2msg + "\nAnda menang, skor menjadi " + str(p1score) + "-" + str(p2score)
                            if p1score == 7:
                                p1msg = p1msg + "\nPermainan dimenangkan oleh anda"
                                p2msg = p2msg + "\nPermainan dimenangkan oleh musuh"
                                send_msg(clients[p1][0], p1msg, "GAME_FINISHED")
                                send_msg(clients[p2][0], p2msg, "GAME_FINISHED")
                                p1.state = "ROOM"
                                p2.state = "ROOM"
                                room.pop()
                                break
                            elif p2score == 7:
                                p1msg = p1msg + "\nPermainan dimenangkan oleh musuh"
                                p2msg = p2msg + "\nPermainan dimenangkan oleh anda"
                                send_msg(clients[p1][0], p1msg, "GAME_FINISHED")
                                send_msg(clients[p2][0], p2msg, "GAME_FINISHED")
                                p1.state = "ROOM"
                                p2.state = "ROOM"
                                room.pop()
                                break
                            p1draw = game.draw("p1")
                            if p1draw is None:
                                p1draw = Card("None")
                            p2draw = game.draw("p2")
                            if p2draw is None:
                                p2draw = Card("None")
                            p1msg = p1msg + ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                             p1draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                            p2msg = p2msg + ("\nBabak " + str(gameround) + "\nDraw anda: " +
                                             p2draw.get_cardtype() + "\nFase wildcard\nHand anda:\n")
                            for x in range(len(p1hand)):
                                p1msg = p1msg + str(x + 1) + ". " + p1hand[x].get_cardtype() + "\n"
                            for x in range(len(p2hand)):
                                p2msg = p2msg + str(x + 1) + ". " + p2hand[x].get_cardtype() + "\n"
                            send_msg(clients[p1][0], p1msg, "INPUT_RESET")
                            send_msg(clients[p2][0], p2msg, "INPUT_RESET")
                            game.set_state("WILDCARD")
                            p1.state = "GAME"
                            p2.state = "GAME"
                            game.set_unready()
                            break
                    else:
                        send_msg(sock_cli, "\nMainkan wildcard sebagai:\n"
                                           "1. Batu\n"
                                           "2. Gunting\n"
                                           "3. Kertas\n", "Wildcard")
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
    for u in userlist:
        if u.username == username_cli:
            sock_cli.send(bytes("Username telah digunakan", "utf-8"))
            sock_cli.close()
            break
    else:
        sock_cli.send(bytes("Selamat datang, " + username_cli, "utf-8"))
        print(username_cli, "joined")
        user = User(username_cli, "LOBBY", (0, 0, 0))
        userlist.append(user)

        thread_cli = threading.Thread(target=read_msg, args=(clients, sock_cli, addr_cli, user, userlist))
        thread_cli.start()

        clients[user] = (sock_cli, addr_cli, thread_cli)
        invitationlist[user] = []
        friendlist[user] = []
