#!/usr/bin/env python3
"""Read-safe hwmon discovery for NZXT Kraken 2023 monitoring."""


def main():
    import glob
    
    base = "/sys/class/hwmon"

    print("=" * 70)
    print("HWMON DISCOVERY REPORT - For GUI wiring")
    print("=" * 70)

    hwmons = sorted(glob.glob(base + "/*"))

    for path in hwmons:
        try:
            name_file = f"{path}/name"
            