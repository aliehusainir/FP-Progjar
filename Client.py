import sys
import socket
import threading
import time


def read_msg(sock_cli):
    while True:
        data, option = sock_cli.recv(65535).decode("utf-8").split("|")
        if len(data) == 0:
            break

        if option == "gambar":
            gambar = open(data, 'wb')
            while True:
                img = socket.recv(65535)
                if not img:
                    break
                gambar.write(img)

        else:
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
hasdeck = False

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
                dest = input("Masukkan username tujuan (ketikkan bcast untuk broadcast pesan): ")
                msg = input("Masukkan lokasi gambar yang akan dikirim: ")
                sock_cli.send(bytes("gambar|{}|{}".format(dest, msg), "utf-8"))
            
            elif option == "Buat room":
                if hasdeck:
                    sock_cli.send(bytes(option, "utf-8"))
                    userstate = "ROOM"
                    time.sleep(1)
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
            option = input("\nApa yang ingin anda lakukan?\n"
                        "Lihat deck\n"
                        "Undang pemain\n"
                        "Mulai permainan\n"
                        "Kembali ke lobi\n"
                        ">> ")
            if option == "Lihat deck":
                sock_cli.send(bytes(option, "utf-8"))
                time.sleep(1)
            elif option == "Undang pemain":
                dest = input("\nMasukkan username yang ingin diundang ke room: \n"
                            ">> ")
                sock_cli.send(bytes("Undang " + dest, "utf-8"))
                time.sleep(1)
            elif option == "Kembali ke lobi":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "LOBBY"
        elif userstate == "ACCEPTING":
            option = input()
            if option == "Kembali ke lobi":
                sock_cli.send(bytes(option, "utf-8"))
                userstate = "LOBBY"
            else:
                sock_cli.send(bytes(option, "utf-8"))
                time.sleep(1)

except KeyboardInterrupt:
    sock_cli.close()
    sys.exit(0)