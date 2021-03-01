import asyncio
import logging
import patterns
import view
import socket
import threading

logging.basicConfig(filename="client.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):
    def __init__(self):
        super().__init__()
        self.username = str()
        self._run = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("192.168.4.116", 50007))
        self.socket.settimeout(0.5)

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
        # Will need to modify this
        # self.add_msg(msg)
        if msg.lower().startswith("/quit"):
            # Command that leads to the closure of the process
            self.send("QUIT")
            raise KeyboardInterrupt
        else:
            self.send(msg)

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def send(self, msg):
        message = msg.encode("utf-8")
        msg_length = len(message)
        send_length = str(msg_length).encode("utf-8")
        send_length += b" " * (64 - len(send_length))
        self.socket.send(send_length)
        self.socket.send(message)

    def run(self):
        # self.send("Hello!")
        # await asyncio.sleep(2)
        # self.send("Hello again!")
        # await asyncio.sleep(2)
        while True:
            try:
                msg_length = self.socket.recv(64).decode("utf-8")
            except socket.timeout as e:
                print("recv timed out, retry later")
                # await asyncio.sleep(0.05)
                continue
            else:
                if msg_length:
                    msg_length = int(msg_length)
                    ##
                    msg_not_received = True
                    while msg_not_received:
                        try:
                            msg = self.socket.recv(msg_length).decode("utf-8")
                        except socket.timeout as e:
                            print("recv timed out, retry later")
                            # await asyncio.sleep(0.05)
                            continue
                        else:
                            msg_not_received = False
                    ##
                    self.add_msg(msg)
                    # await asyncio.sleep(0.05)
                else:
                    # Client connection closed on server end
                    break

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass


def main(args):
    # Pass your arguments where necessary
    client = IRCClient()
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
                # client.run(),
                return_exceptions=True,
            )

        try:
            threading.Thread(target=client.run).start()
            asyncio.run(inner_run())
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(args)
