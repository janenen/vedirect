from typing import Callable


encoding = "utf-8"

error_codes = {
    0: "No error",
    2: "Battery voltage too high",
    17: "Charger temperature too high",
    18: "Charger over current",
    19: "Charger current reversed",
    20: "Bulk time limit exceeded",
    21: "Current sensor issue (sensor bias/sensor broken)",
    26: "Terminals overheated",
    33: "Input voltage too high (solar panel)",
    34: "Input current too high (solar panel)",
    38: "Input shutdown (due to excessive battery voltage)",
    116: "Factory calibration data lost",
    117: "Invalid/incompatible firmware",
    119: "User settings invalid",
}


def conv_error(code):
    return error_codes[int(code)]


device_state_map = {
    0: "Off",
    1: "Low power",
    2: "Fault",
    3: "Bulk",
    4: "Absorption",
    5: "Float",
    6: "Storage",
    7: "Equalize (manual)",
    9: "Inverting",
    11: "Power supply",
    245: "Starting-up",
    246: "Repeated absorption",
    247: "Auto equalize / Recondition",
    248: "BatterySafe",
    252: "External Control",
}


def conv_mode(code):
    return device_state_map[int(code)]


offReasonDecode = {
    0x000: "",
    0x001: "No input power",
    0x002: "Switched off (power switch)",
    0x004: "Switched off (device mode register)",
    0x008: "Remote input",
    0x010: "Protection active",
    0x020: "Paygo",
    0x040: "BMS",
    0x080: "Engine shutdown detection",
    0x100: "Analyzing input voltage",
}
capBleDecode = {
    0x001: "BLE supports switching off",
    0x002: "BLE switching off is permanent",
}
trackerModeDecode = {
    0x000: "Off",
    0x001: "Voltage or current limited",
    0x002: "MPPT Tracker active",
}
alarmReasonDecode = {
    "Low Voltage": 1 << 0,  # 1  0b00000000000001
    "High Voltage": 1 << 1,  # 2  0b00000000000010
    "Low SOC": 1 << 2,  # 4  0b00000000000100
    "Low Starter Voltage": 1 << 3,  # 8  0b00000000001000
    "High Starter Voltage": 1 << 4,  # 16  0b00000000010000
    "Low Temperature": 1 << 5,  # 32  0b00000000100000
    "High Temperature": 1 << 6,  # 64  0b00000001000000
    "Mid Voltage": 1 << 7,  # 128  0b00000010000000
    "Overload": 1 << 8,  # 256  0b00000100000000
    "DC-ripple": 1 << 9,  # 512  0b00001000000000
    "Low V AC out": 1 << 10,  # 1024  0b00010000000000
    "High C AC out": 1 << 11,  # 2048  0b00100000000000
    "Short Circuit": 1 << 12,  # 4096  0b01000000000000
    "BMS Lockout": 1 << 13,  # 8192  0b10000000000000
}

values = {
    "LOAD": {"key": "load"},
    "H19": {"key": "yieldTotal", "mx": 0.01},
    "VPV": {"key": "panelVoltage", "mx": 0.001},
    "ERR": {"key": "error", "f": conv_error},
    "FW": {"key": "firmwareVersion", "mx": 0.01},
    "I": {"key": "current", "mx": 0.001},
    "H21": {"key": "maximumPowerToday", "f": int},  # W
    "IL": {"key": "loadCurrent", "mx": 0.001},
    "PID": {"key": "productId"},
    "H20": {"key": "yieldToday", "mx": 0.01},  # 0.01 kWh
    "H23": {"key": "maximumPowerYesterday", "f": int},  # W
    "H22": {"key": "yieldYesterday", "mx": 0.01},  # 0.01 kWh
    "HSDS": {"key": "daySequenceNumber", "f": int},
    "SER#": {"key": "serialNumber"},
    "V": {"key": "batteryVoltage", "mx": 0.001},
    "CS": {"key": "mode", "f": conv_mode},
    "PPV": {"key": "panelPower", "f": int},
}
divs = {
    "batteries_hdg": ["bmv", "SOC"],
    "batteries_bdy": ["bmv", "V", "I"],
    "solar_hdg": ["mppt", "I"],
    "solar_bdy": ["mppt", "V", "CS", "H20"],
    "vehicle_hdg": ["bmv", "VS"],
    "vehicle_bdy": ["bmv", "Relay"],
    "conv_hdg": ["conv", "I"],
    "conv_bdy": ["conv", "V", "T"],
}
units = {
    "V": "mV",
    "V2": "mV",
    "V3": "mV",
    "VS": "mV",
    "VM": "mV",
    "DM": "%",
    "VPV": "mV",
    "PPV": "W",
    "I": "mA",
    "I2": "mA",
    "I3": "mA",
    "IL": "mA",
    "LOAD": "",
    "T": "°C",
    "P": "W",
    "CE": "mAh",
    "SOC": "%",
    "TTG": "Minutes",
    "Alarm": "",
    "Relay": "",
    "AR": "",
    "OR": "",
    "H1": "mAh",
    "H2": "mAh",
    "H3": "mAh",
    "H4": "",
    "H5": "",
    "H6": "mAh",
    "H7": "mV",
    "H8": "mV",
    "H9": "Seconds",
    "H10": "",
    "H11": "",
    "H12": "",
    "H15": "mV",
    "H16": "mV",
    "H17": "0.01 kWh",
    "H18": "0.01 kWh",
    "H19": "0.01 kWh",
    "H20": "0.01 kWh",
    "H21": "W",
    "H22": "0.01 kWh",
    "H23": "W",
    "ERR": "",
    "CS": "*",
    "BMV": "",
    "FW": "",
    "FWE": "",
    "PID": "",
    "SER#": "",
    "HSDS": "",
    "MODE": "",
    "AC_OUT_V": "0.01 V",
    "AC_OUT_I": "0.1 A",
    "AC_OUT_S": "VA",
    "WARN": "",
    "MPPT": "",
}


def int_base_guess(string_val):
    return int(string_val, 0)


types: dict[str:Callable] = {
    "V": int,
    "VS": int,
    "VM": int,
    "DM": int,
    "VPV": int,
    "PPV": int,
    "I": int,
    "IL": int,
    "LOAD": str,
    "T": int,
    "P": int,
    "CE": int,
    "SOC": int,
    "TTG": int,
    "Alarm": str,
    "Relay": str,
    "AR": int_base_guess,
    "OR": int_base_guess,
    "H1": int,
    "H2": int,
    "H3": int,
    "H4": int,
    "H5": int,
    "H6": int,
    "H7": int,
    "H8": int,
    "H9": int,
    "H10": int_base_guess,
    "H11": int_base_guess,
    "H12": int_base_guess,
    "H13": int_base_guess,
    "H14": int_base_guess,
    "H15": int,
    "H16": int,
    "H17": int,
    "H18": int,
    "H19": int,
    "H20": int,
    "H21": int,
    "H22": int,
    "H23": int,
    "ERR": int_base_guess,
    "CS": int_base_guess,
    "BMV": str,
    "FW": str,
    "PID": str,
    "SER#": str,
    "HSDS": int_base_guess,
    "MODE": int_base_guess,
    "AC_OUT_V": int,
    "AC_OUT_I": int,
    "AC_OUT_S": int,
    "WARN": int_base_guess,
    "MPPT": int_base_guess,
    "MON": int,
}

fmt = {
    "%": ["%", 10, 1],
    "°C": ["°C", 1, 0],
    "0.01 kWh": ["Wh", 0.1, 2],
    "mA": ["A", 1000, 2],
    "mAh": ["Ah", 1000, 2],
    "Minutes": ["Mins", 1, 0],
    "mV": ["V", 1000, 2],
    "Seconds": ["Secs", 1, 0],
    "W": ["W", 1, 0],
}
cs = {"0": "Off", "2": "Fault", "3": "Bulk", "4": "Abs", "5": "Float"}
