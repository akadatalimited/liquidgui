#!/usr/bin/env python3
"""Reusable utilities for applying liquidctl fan curves."""

import json
import os
import re
import shutil
import subprocess
import time

CONFIG_PATH = os.path.expanduser("~/.config/liquidctl_curves.json")

LIQUIDCTL_PATH = shutil.which("liquidctl")
if LIQUIDCTL_PATH is None:
    raise FileNotFoundError(
        "liquidctl executable not found. Please install liquidctl and ensure it is in your PATH."
    )


def list_devices():
    """Enumerate available liquidctl devices and channels."""

    try:
        output = subprocess.check_output([LIQUIDCTL_PATH, "list"], text=True)
    except subprocess.CalledProcessError:
        return []

    devices = []
    current = None
    for line in output.splitlines():
        m_dev = re.match(r"Device\s*#?(\d+):", line)
        if m_dev:
            current = int(m_dev.group(1))
            continue
        m_chan = re.search(r"channel\s+\d+:\s+(\S+)", line)
        if m_chan and current is not None:
            devices.append((current, m_chan.group(1)))
    return devices


def get_curve_from_plot(points):
    """Convert point pairs into liquidctl CLI arguments."""

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


def apply_curve(fan_curve, pump_curve, fan_targets=None, pump_targets=None):
    """Send curves to the controller using liquidctl."""

    fan_targets = fan_targets or [(None, "fan")]
    pump_targets = pump_targets or [(None, "pump")]

    for dev, chan in fan_targets:
        cmd = [LIQUIDCTL_PATH]
        if dev is not None:
            cmd += ["--device", str(dev)]
        cmd += ["set", chan, "speed"] + fan_curve
        subprocess.run(cmd, check=False)

    for dev, chan in pump_targets:
        cmd = [LIQUIDCTL_PATH]
        if dev is not None:
            cmd += ["--device", str(dev)]
        cmd += ["set", chan, "speed"] + pump_curve
        subprocess.run(cmd, check=False)


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

    fan_speed = str(int(fan_speed))
    pump_speed = str(int(pump_speed))

    for dev, chan in fan_targets:
        cmd = [LIQUIDCTL_PATH]
        if dev is not None:
            cmd += ["--device", str(dev)]
        cmd += ["set", chan, "speed", fan_speed]
        subprocess.run(cmd, check=False)

    for dev, chan in pump_targets:
        cmd = [LIQUIDCTL_PATH]
        if dev is not None:
            cmd += ["--device", str(dev)]
        cmd += ["set", chan, "speed", pump_speed]
        subprocess.run(cmd, check=False)


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
