# liquidgui

GUI for Liquidctl fan and pump curves. The tool can enumerate devices with
`liquidctl list` and lets you select multiple fan or pump channels. Selected
targets are saved so the tool can also apply previously saved curves in a
headless mode.

## Headless mode

The script accepts an `--apply` flag to apply saved curves without launching the
GUI. A long-running daemon can be started with `--daemon`, which periodically
sets fan and pump speeds based on the configured curves:

```bash
liquidgui --apply        # apply once and exit
liquidgui --daemon       # run continuously
```

## Standalone binary

A self-contained executable can be produced with [PyInstaller](https://pyinstaller.org/):

```bash
make binary
```

The resulting binary is placed in `dist/liquidgui` and can be run directly:

```bash
./dist/liquidgui --apply
```

## Service integration

Example service files are provided for systemd and SysV init systems. Copy the
appropriate file and enable the service to run the daemon automatically at boot.

### systemd

```
sudo cp etc/systemd/system/liquidgui.service /etc/systemd/system/
sudo systemctl enable liquidgui       # start at boot
sudo systemctl disable liquidgui      # disable
```

### SysV init

```
sudo cp etc/init.d/liquidgui /etc/init.d/
sudo update-rc.d liquidgui defaults   # enable
sudo update-rc.d -f liquidgui remove  # disable
```

