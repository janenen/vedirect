#!/usr/bin/python3
# -*- coding: utf-8 -*-

# continuously publish VE.Direct data to the topic prefix specified

import argparse, os
import paho.mqtt.client as mqtt
from vedirect import VEDirect
import logging

log = logging.getLogger(__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process VE.Direct protocol")
    parser.add_argument("--port", help="Serial port")
    parser.add_argument(
        "--timeout", help="Serial port read timeout", type=int, default="60"
    )
    parser.add_argument(
        "--mqttbroker",
        help="MQTT broker address",
        type=str,
        default="test.mosquitto.org",
    )
    parser.add_argument(
        "--mqttbrokerport", help="MQTT broker port", type=int, default="1883"
    )
    parser.add_argument(
        "--topicprefix", help="MQTT topic prefix", type=str, default="vedirect_device/"
    )
    parser.add_argument(
        "--emulate",
        help="emulate one of [ALL, BMV_600, BMV_700, MPPT, PHX_INVERTER]",
        default="",
        type=str,
    )
    parser.add_argument(
        "--loglevel",
        help="logging level - one of [DEBUG, INFO, WARNING, ERROR, CRITICAL]",
        default="ERROR",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())
    ve = VEDirect(args.port, args.timeout, args.emulate)

    client = mqtt.Client()
    client.connect(args.mqttbroker, args.mqttbrokerport, 60)
    client.loop_start()

    def mqtt_send_callback(packet):
        for key, value in packet.items():
            if key != "SER#":  # topic cannot contain MQTT wildcards
                log.info(f"{args.topicprefix + key}: {value}")
                client.publish(args.topicprefix + key, value)

    ve.read_data_callback(mqtt_send_callback)
