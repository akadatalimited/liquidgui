# liquidgui

GUI for Liquidctl fan and pump curves. The tool can also apply previously
saved curves in a headless mode.

## Headless mode

The script accepts an `--apply` flag to apply saved curves without launching the
GUI:

```bash
liquidgui --apply
```

## Service integration

Example service files are provided for systemd and SysV init systems. Copy the
appropriate file and enable the service to apply curves automatically at boot.

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

