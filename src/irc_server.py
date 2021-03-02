import logging
import socket
import threading

logging.basicConfig(filename="server.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer:
    def __init__(self, host="192.168.4.116", port=50007):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(2)
        self.subscribers = []
        self.nicknames = []

    def add_subscriber(self, conn):
        self.subscribers.append(conn)

    def rm_subscriber(self, conn):
        try:
            self.subscribers.remove(conn)
        except ValueError:
            pass

    def rm_nickname(self, nickname):
        try:
            self.nicknames.remove(nickname)
        except ValueError:
            pass

    def notify(self, msg):
        for s in self.subscribers:
            self.update(s, msg)

    def update(self, conn, msg):
        message = msg.encode("utf-8")
        msg_length = len(message)
        send_length = str(msg_length).encode("utf-8")
        send_length += b" " * (64 - len(send_length))
        conn.send(send_length)
        conn.send(message)

    def handle_client(self, conn, addr):
        print(f"[CONNECTION] Client {addr} has connected.")
        # self.add_subscriber(conn)
        connected = True
        client_nickname = str()
        while connected:
            msg_length = int(conn.recv(64).decode("utf-8"))
            msg = conn.recv(msg_length).decode("utf-8")
            if msg == "QUIT":
                connected = False
            elif msg.startswith("NICK"):
                nickname = msg.split()[1]
                if nickname not in self.nicknames:
                    client_nickname = nickname
                    self.nicknames.append(client_nickname)
                    self.update(
                        conn,
                        f"001 {client_nickname} :Welcome to the Internet Relay Network {client_nickname}!",
                    )
                    self.add_subscriber(conn)
                else:
                    self.update(conn, f"433 * {nickname} :Nickname is already in use.")
            else:
                # Notify all client connections (regular PRIVMSG command)
                self.notify(f":{client_nickname} {msg}")
        self.rm_nickname(client_nickname)
        self.rm_subscriber(conn)
        print(f"[DISCONNECTION] Client {addr} has disconnected.")
        conn.close()

    def start(self):
        print("[STARTING] Server is starting...")
        self.socket.listen()
        print(f"[LISTENING] Server is listening on {self.host}")
        while True:
            try:
                conn, addr = self.socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                raise


def main(args):
    server = IRCServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.debug("Signifies end of process")


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(args)