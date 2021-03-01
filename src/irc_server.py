import asyncio
import logging
import patterns
import socket
import threading

logging.basicConfig(filename="server.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer(patterns.Publisher):
    def __init__(self, host="192.168.4.116", port=50007):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(5)

    def handle_client(self, conn, addr):
        print(f"[CONNECTION] Client {addr} has connected.")
        connected = True
        while connected:
            msg_length = int(conn.recv(64).decode("utf-8"))
            msg = conn.recv(msg_length).decode("utf-8")
            if msg == "QUIT":
                connected = False
            print(f"[SENT BY CLIENT] {msg}")
        print(f"[DISCONNECTION] Client {addr} has disconnected.")
        conn.close()

    def start(self):
        print("[STARTING] Server is starting...")
        self.socket.listen()
        print(f"[LISTENING] Server is listening on {self.host}")
        while True:
            try:
                conn, addr = self.socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                raise


def main(args):
    server = IRCServer()
    try:
        server.start()
    except KeyboardInterrupt as e:
        logger.debug("Signifies end of process")


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(args)