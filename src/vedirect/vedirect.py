#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Forked from karioja at https://github.com/karioja/vedirect
#
# 2019-01-16 JMF Modified for Python 3 and updated protocol from
# https://www.sv-zanshin.com/r/manuals/victron-ve-direct-protocol.pdf
#
# Forked from jmfife https://github.com/jmfife/vedirect in 2025

from enum import Enum, auto
from typing import Any
import serial
import argparse

# from .vedirect_device_emulator import VEDirectDeviceEmulator
import sys
import logging
from . import defines

log = logging.getLogger(__name__)


class ParserState(Enum):
    HEX = auto()
    WAIT_HEADER1 = auto()
    WAIT_HEADER2 = auto()
    IN_KEY = auto()
    IN_VALUE = auto()
    IN_CHECKSUM = auto()


HEADER1 = b"\r"
HEADER2 = b"\n"
HEXMARKER = b":"
DELIMITER = b"\t"


class VEDirect:

    def __init__(self, serialport: str, timeout: float = 60):
        """Constructor for a Victron VEDirect serial communication session.

        Params:
            serialport (str): The name of the serial port to open
            timeout (float): Read timeout value (seconds)
        """
        self.key = b""
        self.value = b""
        self.bytes_sum = 0
        self.state: ParserState = ParserState.WAIT_HEADER1
        self.dict = {}

        self.ser = serial.Serial(port=serialport, baudrate=19200, timeout=timeout)
        self.ser.flushInput()

    def _input(self, byte):
        """Accepts a new byte and tries to finish constructing a record.
        When a record is complete, it will be returned as a dictionary
        """
        if byte == HEXMARKER and self.state != ParserState.IN_CHECKSUM:
            self.state = ParserState.HEX
            # TODO: Implement Hex-Protocol

        if self.state == ParserState.WAIT_HEADER1:
            if byte == HEADER1:
                self.bytes_sum += ord(byte)
                self.state = ParserState.WAIT_HEADER2
            return
        if self.state == ParserState.WAIT_HEADER2:
            if byte == HEADER2:
                self.bytes_sum += ord(byte)
                self.state = ParserState.IN_KEY
            return
        elif self.state == ParserState.IN_KEY:
            self.bytes_sum += ord(byte)
            if byte == DELIMITER:
                if self.key == b"Checksum":
                    self.state = ParserState.IN_CHECKSUM
                else:
                    self.state = ParserState.IN_VALUE
            else:
                self.key += byte
            return None
        elif self.state == ParserState.IN_VALUE:
            self.bytes_sum += ord(byte)
            if byte == HEADER1:
                self.state = ParserState.WAIT_HEADER2
                try:
                    self.dict[self.key.decode(defines.encoding)] = self.value.decode(
                        defines.encoding
                    )
                except UnicodeDecodeError:
                    log.warning(
                        f"Could not decode key {self.key} and value {self.value}"
                    )
                self.key = b""
                self.value = b""
            else:
                self.value += byte
            return
        elif self.state == ParserState.IN_CHECKSUM:
            self.bytes_sum += ord(byte)
            self.key = b""
            self.value = b""
            self.state = ParserState.WAIT_HEADER1
            if self.bytes_sum % 256 == 0:  # <=> not self.bytes_sum & 0xFF
                self.bytes_sum = 0
                dict_copy = self.dict.copy()
                self.dict = {}  # clear the holder - ready for a new record
                return dict_copy
            else:
                # print('Malformed record')
                self.bytes_sum = 0
        elif self.state == ParserState.HEX:
            self.bytes_sum = 0
            if byte == HEADER2:
                self.state = ParserState.WAIT_HEADER1
        else:
            raise AssertionError()

    def typecast(self, payload_dict: dict[str:str]) -> dict[str:Any]:
        new_dict: dict[str:Any] = {}
        for key, val in payload_dict.items():
            try:
                new_dict[key] = {"value": defines.types[key](val)}
                if key in defines.units.keys():
                    new_dict[key]["unit"]=defines.units[key]
            except KeyError:
                print(f"Device sending unknown Key {key} and Value {val}.")
        return new_dict

    def read_data_single(self, flush=True):
        """Wait until we get a single complete record, then return it"""
        if flush:
            self.ser.flushInput()
        while True:
            byte = self.ser.read()
            if byte:
                # got a byte (didn't time out)
                record = self._input(byte)
                if record is not None:
                    return self.typecast(record)

    def read_data_callback(self, callbackfunction, n=-1, **kwargs):
        """Non-blocking service to continuously read records, and when one is formed, call the
        callback function with the record as the first argument.
        """
        while n != 0:
            byte = self.ser.read()
            if byte:
                # got a byte (didn't time out)
                record = self._input(byte)
                if record is not None:
                    callbackfunction(self.typecast(record), **kwargs)
                    if n > 0:
                        n = n - 1

    def read_data_single_callback(self, callbackfunction, **kwargs):
        """Continue to wait until we get a single complete record, then call the callback function with the result."""
        callbackfunction(self.read_data_single(), **kwargs)


def main():
    # provide a simple entry point that streams data from a VEDirect device to stdout
    parser = argparse.ArgumentParser(
        description="Read VE.Direct device and stream data to stdout"
    )
    parser.add_argument("--port", help="Serial port to read from", type=str, default="")
    parser.add_argument(
        "--n",
        help="number of records to read (or default=-1 for infinite)",
        default=-1,
        type=int,
    )
    parser.add_argument(
        "--timeout", help="Serial port read timeout, seconds", type=int, default=60
    )
    parser.add_argument(
        "--loglevel",
        help="logging level - one of [DEBUG, INFO, WARNING, ERROR, CRITICAL]",
        default="ERROR",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())
    if not args.port and not args.emulate:
        print("Must specify a port to listen.")
        sys.exit(1)
    ve = VEDirect(args.port, args.timeout)
    ve.read_data_callback(print, args.n)


if __name__ == "__main__":
    main()
