import asyncio
import logging
import patterns
import view
import socket
import threading
import time
import getpass
import click

logging.basicConfig(filename="client.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):
    def __init__(self, host, port):
        super().__init__()
        self._run = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(0.5)
        self.registered = False
        self.nickname = str()
        self.username = getpass.getuser()

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        if self.registered:
            if msg.lower() == "/quit":
                self.send("PART #global")
                self.send("QUIT")
                raise KeyboardInterrupt
            else:
                self.send(f"PRIVMSG #global :{msg}")
        else:
            if msg.lower() == "/quit":
                self.send("QUIT")
                raise KeyboardInterrupt
            elif msg.lower().startswith("/register"):
                if len(msg.split()) != 2:
                    self.view.put_msg("Error: incorrect command syntax.\n")
                else:
                    nick = msg.split()[1]
                    if len(nick) > 9:
                        self.view.put_msg(
                            "Error: nickname must have a maximum length of 9 characters.\n"
                        )
                    else:
                        self.send(f"NICK {nick}")
                        self.send(f"USER {self.username} * * :realname")
            else:
                pass

    def add_msg(self, nickname, msg):
        self.view.put_msg(f"{time.strftime('%H:%M')} [{nickname}] {msg}\n")

    def send(self, msg):
        message = msg.encode("utf-8")
        msg_length = len(message)
        send_length = str(msg_length).encode("utf-8")
        send_length += b" " * (64 - len(send_length))
        self.socket.send(send_length)
        self.socket.send(message)
        logger.info(f"IRCClient.send -> msg: {msg}")

    def run(self):
        while True:
            try:
                msg_length = self.socket.recv(64).decode("utf-8")
            except socket.timeout:
                continue
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    msg_not_received = True
                    while msg_not_received:
                        try:
                            msg = self.socket.recv(msg_length).decode("utf-8")
                        except socket.timeout:
                            continue
                        else:
                            msg_not_received = False
                    logger.info(f"IRCClient.recv -> msg: {msg}")
                    if msg.startswith("001"):
                        self.view.put_msg(msg.split(":")[1] + "\n")
                        self.registered = True
                        self.nickname = msg.split()[1]
                        self.send("JOIN #global")
                    elif msg.startswith("433"):
                        self.view.put_msg(
                            f"Error: Nickname {msg.split()[2]} already in use. Please try another one.\n"
                        )
                    elif msg.split()[1] == "JOIN":
                        nickname = msg.split()[0][1:]
                        self.add_msg(nickname, "has joined #global.")
                    elif msg.split()[1] == "PART":
                        nickname = msg.split()[0][1:]
                        self.add_msg(nickname, "has left #global.")
                    else:
                        # Regular PRIVMSG to #global
                        nickname = msg.split()[0][1:]
                        msg = msg[1:].split(":")[1]
                        self.add_msg(nickname, msg)
                else:
                    # Client connection gracefully closed on server end
                    break

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass


@click.command()
@click.option(
    "--host",
    required=True,
    type=str,
    help="Target server to initiate a connection to",
)
@click.option("--port", required=True, type=int, help="Target port to use")
def main(host, port):
    client = IRCClient(host=host, port=port)
    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

        async def inner_run():
            await asyncio.gather(
                v.run(),
                return_exceptions=True,
            )

        try:
            threading.Thread(target=client.run).start()
            asyncio.run(inner_run())
        except KeyboardInterrupt:
            logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    main()
