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

I am using poetry v1.7.1

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
$ poetry install
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
  set-rgb-all-keys   Set RGB colour for all keys.
  start-daemon       Start a daemon to update the CPU usage and...
  upload-image       Upload an image to the Epomaker device.
```

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

### Note about interface numbers

I only have my own keyboard to go by, but as far as I can tell there are 3 available HID
interfaces available when the keyboard is plugged in over USB. All 3 of them will work with
this controller HOWEVER using interface 0 interferes with regular usage of the keyboard (eg typing).

I have found interface 1 to be the best to use, but some commands take an option for you to set the
interface number manually if you need to eg:
```console
epomakercontroller start-daemon --interface 2
```

You can also print all the available information about the connected keyboard using the 'dev'
command. Here is an example of the output from my own keyboard:
```console
epomakercontroller dev print_all_info
Printing all available information about the connected keyboard.
WARNING: If this program errors out or you cancel early, the keyboard
              may become unresponsive. It should work fine again if you unplug and plug
               it back in!
[{'interface_number': 0,
  'manufacturer_string': 'ROYUAN',
  'path': b'5-2.3:1.0',
  'product_id': 16400,
  'product_string': 'RT100 Wired',
  'release_number': 1281,
  'serial_number': '',
  'usage': 0,
  'usage_page': 0,
  'vendor_id': 12625},
 {'interface_number': 1,
  'manufacturer_string': 'ROYUAN',
  'path': b'5-2.3:1.1',
  'product_id': 16400,
  'product_string': 'RT100 Wired',
  'release_number': 1281,
  'serial_number': '',
  'usage': 0,
  'usage_page': 0,
  'vendor_id': 12625},
 {'interface_number': 2,
  'manufacturer_string': 'ROYUAN',
  'path': b'5-2.3:1.2',
  'product_id': 16400,
  'product_string': 'RT100 Wired',
  'release_number': 1281,
  'serial_number': '',
  'usage': 0,
  'usage_page': 0,
  'vendor_id': 12625}]
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
