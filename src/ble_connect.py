# ble_connect.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed, Sep  1, 2021  5:05:56 PM

import re
from typing import Dict, Any, List, Optional

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice


async def connect_ble(identifier: Optional[str] = None):

    try:
        # Map of discovered devices indexed by name
        devices: Dict[str, BleakDevice] = {}

        # Scan for devices
        print("Scanning for bluetooth devices...")

        # Scan callback to also catch nonconnectable scan responses
        # pylint: disable=cell-var-from-loop
        def _scan_callback(device: BleakDevice, _: Any) -> None:
            # Add to the dict if not unknown
            if device.name and device.name != "Unknown":
                devices[device.name] = device

        # Scan until we find devices
        matched_devices: List[BleakDevice] = []
            # Now get list of connectable advertisements
        for device in await BleakScanner.discover(timeout=5, detection_callback=_scan_callback):
            if device.name != "Unknown" and device.name is not None:
                devices[device.name] = device

        token = re.compile(r"GoPro [A-Z0-9]{4}" if identifier is None else f"GoPro {identifier}")
        matched_devices = [device for name, device in devices.items() if token.match(name)]
        print(f"Found {len(matched_devices)} matching devices.")

        # Connect to first matching Bluetooth device
        device = matched_devices[0]

        print(f"Establishing BLE connection to {device}...")
        client = BleakClient(device)
        await client.connect(timeout=10)
        print("BLE Connected!")

        print("Switching to USB")
        await client.disconnect()
        return
    
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Connection establishment failed: {exc}")
        print(f"Retrying")

    raise RuntimeError(f"Couldn't establish BLE connection")
