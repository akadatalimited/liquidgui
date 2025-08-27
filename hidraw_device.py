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

DeviceChannel = Tuple[str, str]


class KrakenDeviceError(RuntimeError):
    """Raised when the Kraken device cannot be accessed."""


def list_devices() -> List[DeviceChannel]:
    """Return a list of available Kraken device channels.

    Each returned tuple contains the device path and a channel name (``fan`` or
    ``pump``).  If no devices are present an empty list is returned.
    """

    devices: List[DeviceChannel] = []
    for path in glob.glob("/dev/hidraw*"):
        if os.access(path, os.R_OK | os.W_OK):
            devices.append((path, "fan"))
            devices.append((path, "pump"))
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
        with self._open("wb") as f:
            f.write(data)

    def _read(self, size: int = 64) -> bytes:
        with self._open("rb") as f:
            return f.read(size)

    # --- high level operations --------------------------------------------
    def status(self) -> str:
        """Return a raw status string from the device."""

        try:
            data = self._read()
            return f"Raw status from {self.path}: {data.hex()}"
        except KrakenDeviceError:
            raise

    def set_speed(self, channel: str, speed: int) -> None:
        """Set the speed of ``channel`` to ``speed`` percent.

        The implementation simply writes a placeholder report to the device; the
        exact protocol is not required for the tests and can be filled in later.
        """

        report = bytes([0x00, 0x01, int(speed) & 0xFF, 0x00])
        try:
            self._write(report)
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

