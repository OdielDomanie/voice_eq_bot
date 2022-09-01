import logging
import os
from . import signal_handler
from . import client


token = os.getenv("DISCORD_TOKEN")
if not token:
    print("DISCORD_TOKEN env var is not provided.")
    exit()


handler = logging.StreamHandler()
logger_clipper = logging.getLogger("discord")
logger_clipper.setLevel(logging.INFO)
logger_clipper.addHandler(handler)


if __name__ == "__main__":

    client.run(token)
