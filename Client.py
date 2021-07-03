import sys
import socket
import threading
import time


def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535).decode("utf-8")
        if len(data) == 0:
            break
        print(data)


def check_int(string):
    try:
        if int(string) < 0:
            return False
        return True
    except ValueError:
        return False


sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_cli.connect(("127.0.0.1", 50000))
sock_cli.send(bytes(sys.argv[1], "utf-8"))

thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

userstate = "LOBBY"

while True:
    if userstate == "LOBBY":
        option = input("\nApa yang ingin anda lakukan?\n"
                       "Lihat deck\n"
                       "Buat deck\n"
                       "Kirim pesan\n"
                       "Buat room\n"
                       "Keluar\n"
                       ">> ")
        if option == "Keluar":
            sock_cli.close()
            break
        elif option == "Lihat deck":
            sock_cli.send(bytes("Lihat deck", "utf-8"))
            time.sleep(1)
        elif option == "Buat deck":
            sock_cli.send(bytes("Buat deck", "utf-8"))
            userstate = "DECKBUILDING"
            time.sleep(1)
        elif option == "Kirim pesan":
            pass
        elif option == "Buat room":
            pass
    elif userstate == "DECKBUILDING":
        option = input("\nMasukkan 3 angka yang merupakan jumlah kartu "
                       "Batu, Gunting, dan Kertas yang kamu inginkan:\n")
        newdeck = option.split()
        if len(newdeck) != 3:
            continue
        if check_int(newdeck[0]) and check_int(newdeck[1]) and check_int(newdeck[2]):
            rock = int(newdeck[0])
            paper = int(newdeck[1])
            scissors = int(newdeck[2])
            if rock + paper + scissors == 30:
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "LOBBY"
                time.sleep(1)
