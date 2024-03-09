# UDS Simulator 

## Introduction

This UDS (Unified Diagnostic Services) Simulator is a Python application that demonstrates the basics of UDS communication over a CAN (Controller Area Network) bus. It utilizes the `python-can` library for CAN communication and `tkinter` for the graphical user interface (GUI). The simulator is capable of sending UDS messages, both predefined and random, and receiving messages on a virtual CAN bus (`vcan0`).

## Features

- **Send UDS Messages**: Users can manually input message IDs and data in hexadecimal format to send specific UDS messages.
- **Send Random UDS Messages**: The simulator can generate and send random UDS messages with random IDs and data lengths, demonstrating how UDS might handle various data sizes.
- **Receive Messages**: It continuously listens for incoming CAN messages and displays them in the terminal section of the GUI.
- **ISO-TP (ISO 15765-2) Support**: For messages longer than 7 bytes, the simulator uses the ISO-TP protocol to split the message into multiple frames, demonstrating the handling of multi-frame messages in UDS.

## Requirements

- Python 3.x
- `python-can` library
- Linux environment with `socketcan` support and `vcan0` interface set up

## Installation

### Set up a Virtual CAN Interface:

If not already set up, you need to configure a virtual CAN interface named `vcan0`. This can be done using the following commands:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

### Install python-can:

The python-can library is required for CAN communication. Install it using pip:

```bash
python uds_simulator.py
```

### Run the Simulator:

Clone the repository or download the source code. Navigate to the directory containing the script and run it:

```bash
python uds_simulator.py
```

## Usage

### Start the Simulator:

Launch the simulator. The GUI window will open.

### Send a UDS Message:

- Enter the message ID in hexadecimal format in the "Message ID (hex):" field.
- Enter the data payload in hexadecimal format in the "Data (hex):" field.
- Click "Trimite Mesaj" to send the message.

### Send a Random UDS Message:

Click "Trimite Mesaj Aleatoriu" to automatically generate and send a random UDS message.

### View Incoming Messages:

Incoming messages will be displayed in the terminal section of the GUI.

## Note

This simulator is designed for educational and demonstration purposes. It simplifies certain aspects of UDS and ISO-TP communication for ease of understanding. For comprehensive UDS and CAN implementations, refer to official specifications and advanced libraries.
