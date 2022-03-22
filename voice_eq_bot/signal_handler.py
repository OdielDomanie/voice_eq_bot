"When imported, makes the interpreter raise KeyboardInterrupt when SIGTERM is received."

import signal


def convert_to_sigint(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, convert_to_sigint)
