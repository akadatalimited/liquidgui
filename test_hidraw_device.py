import builtins
import types
import pytest

from hidraw_device import KrakenDevice


class DummyDevice(KrakenDevice):
    def __init__(self):
        self.written = None
        self.path = '/dev/null'

    def _write(self, data: bytes) -> None:  # override to capture
        self.written = data


def test_set_speed_constructs_report_fan():
    dev = DummyDevice()
    dev.set_speed('fan', 50)
    report = bytearray(64)
    report[0] = dev.REPORT_ID
    report[1] = dev.CMD_SET_SPEED
    report[2] = dev.CHANNELS['fan']
    report[3] = 50
    report[-1] = (-sum(report[:-1])) & 0xFF
    assert dev.written == bytes(report)


def test_set_speed_constructs_report_pump():
    dev = DummyDevice()
    dev.set_speed('pump', 75)
    report = bytearray(64)
    report[0] = dev.REPORT_ID
    report[1] = dev.CMD_SET_SPEED
    report[2] = dev.CHANNELS['pump']
    report[3] = 75
    report[-1] = (-sum(report[:-1])) & 0xFF
    assert dev.written == bytes(report)


def test_set_speed_invalid_channel():
    dev = DummyDevice()
    with pytest.raises(ValueError):
        dev.set_speed('invalid', 10)


def test_set_speed_invalid_speed():
    dev = DummyDevice()
    with pytest.raises(ValueError):
        dev.set_speed('fan', 200)


def test_set_curve_constructs_report():
    dev = DummyDevice()
    curve = [30, 40, 50, 60]
    dev.set_curve('fan', curve)
    report = bytearray(64)
    report[0] = dev.REPORT_ID
    report[1] = dev.CMD_SET_CURVE
    report[2] = dev.CHANNELS['fan']
    report[3] = 2
    report[4:8] = bytes(curve)
    report[-1] = (-sum(report[:-1])) & 0xFF
    assert dev.written == bytes(report)


def test_set_curve_invalid_channel():
    dev = DummyDevice()
    with pytest.raises(ValueError):
        dev.set_curve('invalid', [20, 30])


def test_set_curve_odd_length():
    dev = DummyDevice()
    with pytest.raises(ValueError):
        dev.set_curve('fan', [20, 30, 40])


def test_set_curve_invalid_speed():
    dev = DummyDevice()
    with pytest.raises(ValueError):
        dev.set_curve('fan', [20, 150])
