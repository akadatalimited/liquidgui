#!/usr/bin/env python3
"""Reusable utilities for applying fan curves via hidraw."""

import json
import os
import re
import subprocess
import time
from typing import List, Tuple

from hidraw_device import (
    KrakenDevice,
    KrakenDeviceError,
    list_devices as hid_list_devices,
)

CONFIG_PATH = os.path.expanduser("~/.config/liquidctl_curves.json")


def list_devices():
    """Enumerate available Kraken HID devices and channels."""
    return hid_list_devices()


def get_curve_from_plot(points):
    """Convert point pairs into a flat list of integers."""
    return [str(int(x)) for pair in points for x in pair]


def load_curve_config():
    """Load saved fan and pump curves from disk."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return (
                data.get("fan"),
                data.get("pump"),
                data.get("fan_targets", []),
                data.get("pump_targets", []),
            )
    return None, None, [], []


def _default_targets(channel: str) -> List[Tuple[str, str]]:
    return [
        (path, chan)
        for path, chan in hid_list_devices()
        if chan == channel
    ]


def apply_curve(fan_curve, pump_curve, fan_targets=None, pump_targets=None):
    """Send curves to the controller using the hidraw device."""

    fan_targets = fan_targets or _default_targets("fan")
    pump_targets = pump_targets or _default_targets("pump")

    fan_curve = list(map(int, fan_curve))
    pump_curve = list(map(int, pump_curve))

    for path, chan in fan_targets:
        try:
            KrakenDevice(path).set_curve(chan, fan_curve)
        except KrakenDeviceError as exc:
            print(f"Error applying fan curve to {path}:{chan}: {exc}")

    for path, chan in pump_targets:
        try:
            KrakenDevice(path).set_curve(chan, pump_curve)
        except KrakenDeviceError as exc:
            print(f"Error applying pump curve to {path}:{chan}: {exc}")


def apply_saved_curves():
    """Apply previously saved curves without launching the GUI."""
    fan_points, pump_points, fan_targets, pump_targets = load_curve_config()
    if not fan_points or not pump_points:
        print(f"No curve configuration found at {CONFIG_PATH}")
        return

    fan_vals = get_curve_from_plot(fan_points)
    pump_vals = get_curve_from_plot(pump_points)
    apply_curve(fan_vals, pump_vals, fan_targets, pump_targets)


def interpolate_curve(points, temp):
    """Interpolate speed from curve points for the given temperature."""
    if not points:
        return 0
    if temp <= points[0][0]:
        return points[0][1]
    if temp >= points[-1][0]:
        return points[-1][1]
    for (t1, s1), (t2, s2) in zip(points, points[1:]):
        if t1 <= temp <= t2:
            ratio = (temp - t1) / (t2 - t1)
            return s1 + ratio * (s2 - s1)
    return points[-1][1]


def read_cpu_temp():
    """Return current CPU temperature in Celsius."""
    try:
        output = subprocess.check_output(["sensors"], text=True)
        match = re.search(r"\+([0-9]+(?:\.[0-9]+)?)°C", output)
        if match:
            return float(match.group(1))
    except subprocess.CalledProcessError:
        pass
    return None


def apply_speeds(fan_speed, pump_speed, fan_targets, pump_targets):
    """Set fan and pump speeds directly."""
    fan_targets = fan_targets or _default_targets("fan")
    pump_targets = pump_targets or _default_targets("pump")

    fan_speed = int(fan_speed)
    pump_speed = int(pump_speed)

    for path, chan in fan_targets:
        try:
            KrakenDevice(path).set_speed(chan, fan_speed)
        except KrakenDeviceError as exc:
            print(f"Error setting fan speed on {path}:{chan}: {exc}")

    for path, chan in pump_targets:
        try:
            KrakenDevice(path).set_speed(chan, pump_speed)
        except KrakenDeviceError as exc:
            print(f"Error setting pump speed on {path}:{chan}: {exc}")


def run_daemon(interval=5):
    """Continuously apply curves based on current CPU temperature."""

    fan_points, pump_points, fan_targets, pump_targets = load_curve_config()
    if not fan_points or not pump_points:
        print(f"No curve configuration found at {CONFIG_PATH}")
        return

    while True:
        temp = read_cpu_temp()
        if temp is not None:
            fan_speed = interpolate_curve(fan_points, temp)
            pump_speed = interpolate_curve(pump_points, temp)
            apply_speeds(fan_speed, pump_speed, fan_targets, pump_targets)
        time.sleep(interval)
