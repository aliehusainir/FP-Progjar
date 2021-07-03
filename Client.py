import sys
import socket
import threading


def read_msg(sock_cli):
    while True:
        data = sock_cli.recv(65535).decode("utf-8")
        if len(data) == 0:
            break
        print(data)


sock_cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_cli.connect(("127.0.0.1", 50000))
sock_cli.send(bytes(sys.argv[1], "utf-8"))

thread_cli = threading.Thread(target=read_msg, args=(sock_cli,))
thread_cli.start()

while True:
    option = input("\nApa yang ingin anda lakukan?\n"
                   "Buat deck\n"
                   "Kirim pesan\n"
                   "Buat room\n"
                   "Keluar\n"
                   ">> ")

    if option == "Keluar":
        sock_cli.close()
        break
    elif option == "Buat deck":
        pass
    elif option == "Kirim pesan":
        pass
    elif option == "Buat room":
        pass
