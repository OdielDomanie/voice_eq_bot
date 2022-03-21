import logging
import os
from . import client


token = os.getenv("DISCORD_TOKEN")
assert token


handler = logging.StreamHandler()
logger_clipper = logging.getLogger("discord")
logger_clipper.setLevel(logging.INFO)
logger_clipper.addHandler(handler)


if __name__ == "__main__":
    
    client.run(token)
