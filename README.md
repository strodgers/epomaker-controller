# Epomakercontroller
![PyPI](https://img.shields.io/pypi/v/EpomakerController.svg)

A CLI tool to interact with an [Epomaker RT100](https://epomaker.com/products/epomaker-rt100) keyboard that comes with a small screen attached. Some features will probably also work with the TH80.

This project is still very rough around the edges!

NOTE!!!: This currently only works over the USB connection!

## Features

- Upload images to the RT100 screen
- Send arbitrary numbers to the CPU and Temeprature displays on the screen
- Set RGB patterns on the keyboard
- Set individual key colours
- Start a daemon to continuously update the CPU and temperature on the screen

## Requirements

Requires python3-tkinter installed eg
```
sudo apt-get install python3-tkinter
```

## Installation
I suggest using conda or a python virtual env, tested on python 3.10 and 3.12:

_Epomakercontroller_ package is available on [PyPi](https://pypi.org/project/EpomakerController/)

```console
$ python3.10 -m venv epomaker
$ source epomaker/bin/activate
$ pip install EpomakerController
```

You can also install _Epomakercontroller_ via poetry

```console
$ sudo apt install poetry
$ git clone https://github.com/strodgers/epomaker-controller
$ cd epomaker-controller
$ python3.10 -m venv epomaker
$ source epomaker/bin/activate
$ poetry install --only main
```

## Usage

```console
$ epomakercontroller
Usage: epomakercontroller [OPTIONS] COMMAND [ARGS]...

  A simple CLI for the EpomakerController.

Options:
  --help  Show this message and exit.

Commands:
  cycle-light-modes  Cycle through the light modes.
  dev                Various dev tools.
  list-temp-devices  List available temperature devices.
  send-cpu           Send CPU usage percentage to the Epomaker screen.
  send-temperature   Send temperature to the Epomaker screen.
  send-time          Send the current time to the Epomaker device.
  set-keys           Open a simple GUI to set individual key colours.
  set-rgb-all-keys   Set RGB colour for all keys.
  start-daemon       Start a daemon to update the CPU usage and...
  upload-image       Upload an image to the Epomaker device.
```

There is a basic GUI to set key colours, it currently only uses a UK ISO layout. You can open it with:
```
epomakercontroller set-keys
```
![Screenshot from 2024-09-22 00-42-07](https://github.com/user-attachments/assets/6a105262-a51d-4969-8b46-5e32c042473b)

You can click on various keys, then press 'Enter' on your keyboard to select a colour:

![Screenshot from 2024-09-22 00-41-59](https://github.com/user-attachments/assets/e726110b-3a22-416c-8a4f-d0ef6b4cc652)


### Permissions
In order to communicate with your keyboard without having to use sudo, you can
use the tool to generate a udev rule for the connected RT100:
```console
epomakercontroller dev --udev
```
You will need to enter your password when prompted.

### CPU/Temperature display
The temperature on the Epomaker screen is supposed to be for the weather, but I thought it was more
useful to display the temperature of some device on the host machine. You will need to find out
the label used by a sensor on your machine, which you can do by:
```console
$ epomakercontroller list-temp-devices

Temperature key: nvme
  Label: Composite
  Current: 35.85°C
  High: 82.85°C
  Critical: 89.85°C
  Label: Composite
  Current: 44.85°C
  High: 82.85°C
  Critical: 89.85°C

Temperature key: amdgpu
  Label: edge
  Current: 40.0°C
  High: N/A°C
  Critical: N/A°C

Temperature key: k10temp
  Label: Tctl
  Current: 44.5°C
  High: N/A°C
  Critical: N/A°C
  Label: Tccd1
  Current: 39.0°C
  High: N/A°C
  Critical: N/A°C

Temperature key: mt7921_phy0
  Label: N/A
  Current: 28.0°C
  High: N/A°C
  Critical: N/A°C
```

Then you can start the daemon with the corresponding label, eg:
```console
epomakercontroller start-daemon k10temp
```

Alternatively leave the label blank to disable and only do CPU usage:
```console
epomakercontroller start-daemon
```

The daemon will also update the date and time once when it starts

### Show connected devices

You can print all the available information about the connected keyboard using the 'dev'
command. Here is an example of the output from my own keyboard:
```console
epomakercontroller dev --print
Printing all available information about the connected keyboard.
WARNING: If this program errors out or you cancel early, the keyboard
              may become unresponsive. It should work fine again if you unplug and plug
               it back in!
[
  {
    "path": "1-7.3:1.0",
    "vendor_id": "0x3151",
    "product_id": "0x4010",
    "serial_number": "",
    "release_number": 1281,
    "manufacturer_string": "ROYUAN",
    "product_string": "RT100 Wired",
    "usage_page": 0,
    "usage": 0,
    "interface_number": 0
  },
  {
    "path": "1-7.3:1.1",
    "vendor_id": "0x3151",
    "product_id": "0x4010",
    "serial_number": "",
    "release_number": 1281,
    "manufacturer_string": "ROYUAN",
    "product_string": "RT100 Wired",
    "usage_page": 0,
    "usage": 0,
    "interface_number": 1
  },
  {
    "path": "1-7.3:1.2",
    "vendor_id": "0x3151",
    "product_id": "0x4010",
    "serial_number": "",
    "release_number": 1281,
    "manufacturer_string": "ROYUAN",
    "product_string": "RT100 Wired",
    "usage_page": 0,
    "usage": 0,
    "interface_number": 2
  }
]
```

## TODO
- Support bluetooth/2.4Ghz
- Upload GIFs
- Macros

## Contributing

Contributions are very welcome.

## License

Distributed under the terms of the [MIT license][license],
_Epomakercontroller_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

<!-- github-only -->

[license]: https://github.com/imp3ga/EpomakerController/blob/main/LICENSE
[contributor guide]: https://github.com/imp3ga/EpomakerController/blob/main/CONTRIBUTING.md
[command-line reference]: https://EpomakerController.readthedocs.io/en/latest/usage.html
