# liquidgui

`liquidgui` is a Python/Tk fan-control GUI for Linux that auto-detects:

- NZXT Kraken AIO controls through `liquidctl`
- readable `hwmon` temperature sensors
- writable motherboard `hwmon` PWM fan headers

Each detected control gets its own saved Bezier curve. The GUI can drive AIO
pump and fan channels alongside motherboard fan headers from the same editor.

## Current behavior

- auto-detects available sensors and writable controls at runtime
- supports per-control Bezier curves with automatic point propagation on the Y axis
- saves curves in `~/.config/liquidgui_curves.json`
- migrates older `~/.config/liquidctl_curves.json` fan and pump curves
- uses `sudo` for control writes at the moment, which keeps development simple on local machines

## Usage

Run the GUI:

```bash
./liquidgui
```

Run with auto-reload for development:

```bash
./liquidgui --dev
```

Print detected sensors and controls without opening the GUI:

```bash
./liquidgui --dump-detect
```

## Permissions

Access to Kraken control usually requires either a working udev rule or root.
A sample `liquidctl` udev rule is provided in `etc/udev/rules.d/60-liquidctl.rules`.

Install and reload it with:

```bash
sudo cp etc/udev/rules.d/60-liquidctl.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

On Arch Linux, adjust the group in the rule if you do not use `plugdev`.

## Motherboard fan support

Motherboard fan control depends on the kernel exposing writable PWM nodes under
`/sys/class/hwmon`. If AIO controls appear but motherboard headers do not, you
may need a board-specific driver.

For Nuvoton NCT6687/NCT6687D based boards, see:

- `https://github.com/akadata/nct6687d`
- this is the documentation source used for this project
- the Akadata tree was forked from `https://github.com/Fred78290/nct6687d`

Once the driver is loaded and writable `pwmN` files appear in `hwmon`,
`liquidgui` will pick them up automatically as `Motherboard fan 1`, `fan 2`,
and so on.

## Development

Useful checks:

```bash
python3 -m py_compile liquidgui monitor.py
```

The launcher script is `liquidgui`, and the application logic lives in
`monitor.py`.
