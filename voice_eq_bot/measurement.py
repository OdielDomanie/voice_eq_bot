import math
from typing import Any
import numpy as np
import pyloudnorm as pyln


def amp_to_db(amp, max_amp=2**16):
    return 20 * math.log10(amp / max_amp)


MIN_DB = -60
MAX_DB = 0
BOOST_DB = 6


def db_to_dc_percent(db: float) -> float:
    "Convert relative decibel to Discord percent, where 0 dB = 100%"
    # https://github.com/discord/perceptual
    if db <= -60:
        return 0
    elif db <= MAX_DB:
        return (db - MIN_DB) / (MAX_DB - MIN_DB)
    else:  # db > MAX_DB
        return 1 + (db - MAX_DB) / (BOOST_DB - MAX_DB)


def dc_percent_to_db(percent: float) -> float:
    "Convert Discord volume percent to relative decibel, where 0 dB = 100%"
    # https://github.com/discord/perceptual
    if percent == 0:
        return float("-inf")
    elif percent <= 1:
        return percent * (MAX_DB - MIN_DB) + MIN_DB
    else:  # percent > 1:
        return percent * (BOOST_DB - MAX_DB) + MAX_DB


def loudness(audio: np.ndarray, sr: int) -> float:
    """Given float pcm, return LUFS loudness value.
    Can return 'ValueError: Audio must be have length greater than the block size'
    """
    # ITU-R BS.1770-4
    meter = pyln.Meter(sr)
    # Can return:
    #   ValueError: Audio must be have length greater than the block size
    return meter.integrated_loudness(audio)


def float_to_array(pcm: bytes, channels: int) -> np.ndarray[Any, np.dtype[np.float32]]:
    "Create a numpy array of floats given bytes."
    audio_arr_raw: np.ndarray = np.frombuffer(pcm, np.float32)
    audio_arr = audio_arr_raw.reshape((-1, channels))
    return audio_arr
