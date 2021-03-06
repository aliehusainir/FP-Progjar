import sys
import socket
import threading
import time


def read_msg(sock_cli):
    global userstate, isguest, hasguest, hasinput
    while True:
        data, option = sock_cli.recv(65535).decode("utf-8").split("|")
        if len(data) == 0:
            break
        if option == "gambar":
            gambar = open(data, 'wb')
            while True:
                img = socket.recv(1024)
                if not img:
                    break
                gambar.write(img)
        elif option == "TO_ROOM":
            userstate = "ROOM"
            isguest = True
            print(data)
        elif option == "TO_LOBBY":
            userstate = "LOBBY"
            isguest = False
            print(data)
        elif option == "GUEST_ENTERS":
            hasguest = True
            print(data)
        elif option == "GUEST_LEAVES":
            hasguest = False
            print(data)
        elif option == "TO_GAME":
            userstate = "GAME"
            print(data)
        elif option == "INPUT_RECEIVED":
            hasinput = True
            print(data)
        elif option == "INPUT_RESET":
            hasinput = False
            print(data)
        elif option == "GAME_FINISHED":
            userstate = "ROOM"
            hasinput = False
            print(data)
        else:
            print(data)


def check_int(string):
    try:
        if int(string) < 0:
            return False
        return True
    except ValueError:
        return False


def check_input(string):
    string = string.split()
    if len(string) != len(set(string)):
        return False
    for n in string:
        try:
            if int(n)-1 < 0:
                return False
        except ValueError:
            return False
    return True


sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_cli.connect(("127.0.0.1", 50000))
sock_cli.send(bytes(sys.argv[1], "utf-8"))
response = sock_cli.recv(65535).decode()
print(response)
if response == "Username telah digunakan":
    sock_cli.close()
    exit()

thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

userstate = "LOBBY"
hasdeck = False
isguest = False
hasguest = False
hasinput = False

try:
    while True:
        if userstate == "LOBBY":
            option = input("\nApa yang ingin anda lakukan?\n"
                           "Lihat deck\n"
                           "Buat deck\n"
                           "Tambah teman\n"
                           "Kirim pesan privat\n"
                           "Kirim pesan broadcast\n"
                           "Kirim gambar\n"
                           "Buat room\n"
                           "Terima undangan\n"
                           "Keluar\n"
                           ">> ")
            if option == "Keluar":
                sock_cli.close()
                break
            elif option == "Lihat deck":
                sock_cli.send(bytes(option, "utf-8"))
                time.sleep(1)
            elif option == "Buat deck":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "DECKBUILDING"
                time.sleep(1)
            elif option == "Tambah teman":
                username = input("Masukkan username yang ingin ditambahkan sebagai teman: ")
                sock_cli.send(bytes("add|{}".format(username), "utf-8"))
            elif option == "Kirim pesan privat":
                dest = input("Masukkan username tujuan: ")
                msg = input("Masukkan pesan anda: ")
                sock_cli.send(bytes("chat|{}|{}".format(dest, msg), "utf-8"))
            elif option == "Kirim pesan broadcast":
                msg = input("Masukkan pesan anda: ")
                sock_cli.send(bytes("bcast|{}".format(msg), "utf-8"))
            elif option == "Kirim gambar":
                dest = input("Masukkan username tujuan: ")
                msg = input("Masukkan nama gambar yang akan dikirim: ")
                sock_cli.send(bytes("gambar|{}|{}".format(dest, msg), "utf-8"))
            elif option == "Buat room":
                if hasdeck:
                    sock_cli.send(bytes(option, "utf-8"))
                    userstate = "ROOM"
                else:
                    print("Silakan buat deck terlebih dahulu")
            elif option == "Terima undangan":
                if hasdeck:
                    sock_cli.send(bytes(option, "utf-8"))
                    userstate = "ACCEPTING"
                    time.sleep(1)
                else:
                    print("Silakan buat deck terlebih dahulu")
            else: 
                print("Perintah yang anda masukkan tidak dikenali")
        elif userstate == "DECKBUILDING":
            option = input("\nMasukkan 3 angka yang merupakan jumlah kartu "
                           "Batu, Gunting, dan Kertas yang kamu inginkan:\n"
                           ">> ")
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
                    hasdeck = True
                    time.sleep(1)
        elif userstate == "ROOM":
            if not isguest:
                option = input("\nApa yang ingin anda lakukan?\n"
                               "Lihat deck\n"
                               "Undang pemain\n"
                               "Mulai permainan\n"
                               "Kembali ke lobi\n"
                               ">> ")
            else:
                option = input("\nApa yang ingin anda lakukan?\n"
                               "Lihat deck\n"
                               "Siap bermain\n"
                               "Kembali ke lobi\n"
                               ">> ")
            if option == "Lihat deck":
                sock_cli.send(bytes(option, "utf-8"))
                time.sleep(1)
            elif option == "Undang pemain":
                if hasguest:
                    print("Sudah ada pemain lain di dalam room")
                else:
                    dest = input("\nMasukkan username yang ingin diundang ke room: \n"
                                 ">> ")
                    sock_cli.send(bytes("Undang " + dest, "utf-8"))
                    time.sleep(1)
            elif option == "Mulai permainan":
                if not hasguest:
                    print("Menunggu lawan memasuki room")
                else:
                    sock_cli.send(bytes(option, "utf-8"))
                    userstate = "READY"
            elif option == "Siap bermain":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "READY"
            elif option == "Kembali ke lobi":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "LOBBY"
                isguest = False
                hasguest = False
        elif userstate == "ACCEPTING":
            option = input(">> ")
            if option == "Kembali ke lobi":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "LOBBY"
            else:
                sock_cli.send(bytes(option, "utf-8"))
                time.sleep(1)
        elif userstate == "READY":
            if not (hasguest or isguest):
                sock_cli.send(bytes("Batalkan", "utf-8"))
                userstate = "ROOM"
                continue
            option = input("\nMenunggu lawan bersiap\n"
                           "Batalkan\n"
                           ">>")
            if option == "Batalkan":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "ROOM"
        elif userstate == "GAME":
            if hasinput:
                time.sleep(1)
            else:
                option = input(">> ")
                if not option:
                    sock_cli.send(bytes("\n", "utf-8"))
                    time.sleep(1)
                elif check_input(option):
                    sock_cli.send(bytes(option, "utf-8"))
                    time.sleep(1)

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)
