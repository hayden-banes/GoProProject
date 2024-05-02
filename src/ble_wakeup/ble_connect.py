# ble_connect.py/Open GoPro, Version 2.0 (C) Copyright 2021 GoPro, Inc. (http://gopro.com/OpenGoPro).
# This copyright was auto-generated on Wed, Sep  1, 2021  5:05:56 PM

import re
from typing import Dict, Any, List, Optional

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice as BleakDevice
from ble_wakeup import logger


async def connect_ble(identifier: Optional[str] = None):

    try:
        # Map of discovered devices indexed by name
        devices: Dict[str, BleakDevice] = {}

        # Scan for devices
        logger.info("Scanning for bluetooth devices...")

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
        # Log every device we discovered
        # for d in devices:
        #     logger.info(f"\tDiscovered: {d}")
        # Now look for our matching device(s)
        token = re.compile(r"GoPro [A-Z0-9]{4}" if identifier is None else f"GoPro {identifier}")
        matched_devices = [device for name, device in devices.items() if token.match(name)]
        logger.info(f"Found {len(matched_devices)} matching devices.")

        # Connect to first matching Bluetooth device
        device = matched_devices[0]

        logger.info(f"Establishing BLE connection to {device}...")
        client = BleakClient(device)
        await client.connect(timeout=10)
        logger.info("BLE Connected!")
        # logger.info("Attempting to pair...")
        # try:
        #     await client.pair()
        # except NotImplementedError:
        #     # This is expected on Mac
        #     pass
        # logger.info("Pairing complete!")

        logger.info("Disconnecting and switching to USB")
        await client.disconnect()
        return
    
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(f"Connection establishment failed: {exc}")
        logger.warning(f"Retrying")

    raise RuntimeError(f"Couldn't establish BLE connection")
