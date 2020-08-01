"""This module contains utility functions that supports Reed Solomon Coding."""

from reedsolo import RSCodec, ReedSolomonError
import numpy as np


# Supoorts Reed Soloomon codes

def example():
    rsc = RSCodec(10)

    # Encoding
    raw_list = rsc.encode([1, 2, 3, 4])
    print(raw_list)
    byte_array = rsc.encode(bytearray([1, 2, 3, 4]))
    print(byte_array)
    b_str = rsc.encode(b'hello world')
    print(b_str)
    # Note that chunking is supported transparently to encode any string length.

    # Decoding (repairing)
    print(rsc.decode(b'hello world\xed%T\xc4\xfd\xfd\x89\xf3\xa8\xaa')[0])
    print(rsc.decode(b'heXlo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')[0])  # 3 errors
    print(rsc.decode(b'hXXXo worXd\xed%T\xc4\xfdX\x89\xf3\xa8\xaa')[0])  # 5 errors
    try:
        rsc.decode(b'hXXXo worXd\xed%T\xc4\xfdXX\xf3\xa8\xaa')[0]  # 6 errors - fail
    except ReedSolomonError:
        print("error happened")


# for the combined messages
def deserialize(input: bytearray, rsc: RSCodec = RSCodec(10), datatype="int64"):

    return


def serialize(title: str, message, rsc: RSCodec = RSCodec(10)) -> bytearray:
    return

