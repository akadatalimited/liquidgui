#!/usr/bin/env python3
"""Minimal NZXT Kraken 2023 HID interface.

This module communicates with the cooler using the hidraw interface so that the
rest of the project can operate without calling the external ``liquidctl``
program.  The implementation is intentionally lightweight and is designed to
fail gracefully when the hardware is not present.
"""

from __future__ import annotations

import glob
import os
from typing import List, Tuple


NZXT_VENDOR_ID = "1e71"

DeviceChannel = Tuple[str, str]


class KrakenDeviceError(RuntimeError):
    """Raised when the Kraken device cannot be accessed."""


def list_devices() -> List[DeviceChannel]:
    """Return a list of available Kraken device channels.

    Each returned tuple contains the device path and a channel name (``fan`` or
    ``pump``).  Only devices matching the NZXT vendor ID are returned.  If no
    devices are present an empty list is returned.
    """

    devices: List[DeviceChannel] = []
    for path in glob.glob("/dev/hidraw*"):
        if not os.access(path, os.R_OK | os.W_OK):
            continue

        uevent_path = f"/sys/class/hidraw/{os.path.basename(path)}/device/uevent"
        try:
            with open(uevent_path) as f:
                props = dict(line.strip().split("=", 1) for line in f if "=" in line)
        except OSError:  # pragma: no cover - depends on system
            continue

        hid_id = props.get("HID_ID", "")
        try:
            _bus, vendor, product = hid_id.split(":")
            product = product.split(".")[0]
        except ValueError:
            continue

        if vendor.lower() != NZXT_VENDOR_ID:
            continue

        phys = props.get("HID_PHYS", "")
        channel = "pump" if phys.endswith("/input1") else "fan"
        devices.append((path, channel))

    return devices


class KrakenDevice:
    """Simple wrapper around a hidraw device file."""

    def __init__(self, path: str | None = None) -> None:
        if path is None:
            devices = list_devices()
            if not devices:
                raise KrakenDeviceError("No Kraken device detected")
            path = devices[0][0]
        self.path = path

    # --- low level helpers -------------------------------------------------
    def _open(self, mode: str):
        try:
            return open(self.path, mode, buffering=0)
        except OSError as exc:  # pragma: no cover - depends on system
            raise KrakenDeviceError(f"Unable to access {self.path}: {exc}") from exc

    def _write(self, data: bytes) -> None:
        """Write ``data`` to the hidraw device.

        Any :class:`OSError` raised while attempting to write (for example, a
        ``BrokenPipeError`` when no device is present) is converted into a
        :class:`KrakenDeviceError` so that higher level callers can handle the
        failure gracefully.
        """

        try:
            with self._open("wb") as f:
                f.write(data)
        except OSError as exc:  # pragma: no cover - depends on system
            raise KrakenDeviceError(f"Unable to write to {self.path}: {exc}") from exc

    def _read(self, size: int = 64) -> bytes:
        try:
            with self._open("rb") as f:
                return f.read(size)
        except OSError as exc:  # pragma: no cover - depends on system
            raise KrakenDeviceError(f"Unable to read from {self.path}: {exc}") from exc

    # --- high level operations --------------------------------------------
    def status(self) -> str:
        """Return a raw status string from the device."""

        try:
            data = self._read()
            return f"Raw status from {self.path}: {data.hex()}"
        except KrakenDeviceError:
            raise

    REPORT_ID = 0x21
    CMD_SET_SPEED = 0x01
    CHANNELS = {"fan": 0x00, "pump": 0x01}

    def set_speed(self, channel: str, speed: int) -> None:
        """Set the speed of ``channel`` to ``speed`` percent.

        The Kraken 2023 protocol uses a 64‑byte HID report.  The first byte is the
        report ID, followed by a command identifier, the channel selector and the
        desired speed.  The last byte of the report is an 8‑bit checksum, defined as
        the two's complement of the sum of the preceding bytes.
        """

        if channel not in self.CHANNELS:
            raise ValueError(f"Unsupported channel: {channel}")
        if not 0 <= int(speed) <= 100:
            raise ValueError(f"Invalid speed: {speed}")

        report = bytearray(64)
        report[0] = self.REPORT_ID
        report[1] = self.CMD_SET_SPEED
        report[2] = self.CHANNELS[channel]
        report[3] = int(speed) & 0xFF
        report[-1] = (-sum(report[:-1])) & 0xFF

        try:
            self._write(bytes(report))
        except KrakenDeviceError:
            raise

    def set_curve(self, channel: str, curve: List[int]) -> None:
        """Apply a curve defined by ``curve`` to ``channel``.

        ``curve`` is a flat list of temperature/speed pairs.
        """

        for _temp, speed in zip(curve[::2], curve[1::2]):
            self.set_speed(channel, speed)


def get_status() -> str:
    """Convenience wrapper returning the status of the first device."""

    devices = list_devices()
    if not devices:
        raise KrakenDeviceError("No Kraken device accessible")
    return KrakenDevice(devices[0][0]).status()

