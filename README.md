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

A self-contained executable can be produced with [PyInstaller](https://pyinstaller.org/).
Ensure PyInstaller is installed in the active Python environment (e.g., `python -m pip install PyInstaller`):

```bash
make binary
```

The resulting binary is placed in `dist/liquidgui` and can be run directly:

```bash
./dist/liquidgui --apply
```

## Permissions

Access to the Kraken device normally requires root.  A udev rule is provided so
members of the `plugdev` group can run the tool without `sudo`.

### Enabling the udev rule

1. Create the `plugdev` group if it does not already exist:

   ```bash
   sudo groupadd -f plugdev
   ```

2. Add your user to the group:

   ```bash
   sudo usermod -aG plugdev "$USER"
   ```

3. Install the rule and reload udev:

   ```bash
   sudo cp etc/udev/rules.d/60-liquidctl.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

4. Log out and back in for the new group to take effect.

5. Verify permissions on the device:

   ```bash
   udevadm info --query=property --name=/dev/hidraw0 | grep -E 'GROUP|MODE'
   ls -l /dev/hidraw0
   ```

   Replace `/dev/hidraw0` with the path to your Kraken device; the output should
   show the `plugdev` group.

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

