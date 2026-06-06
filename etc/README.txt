#!/bin/bash
# Deploy liquidctl udev rules for NZXT Kraken pump control access
sudo cp /srv/test/etc/*.rules /etc/udev/rules.d/ 2>&1 || { echo "Copy failed: $?" ; exit 1; }
sudo systemctl daemon-reload
echo "Loaded. Run ls -la bash.d/**pwm_control.rules now and then run sudo udevadm control --reload-paths to verify rules active in device tree for liquidctl pump duty adjustments from GUI monitor app running on this Linux workstation right here
