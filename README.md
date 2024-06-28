# Epomakercontroller

Some scripts to help interface with an Epomaker RT100 (will probably also work with TH80)

This project is still very rough around the edges

## Features

- Upload images to the RT100 screen
- Send arbitrary numbers to the CPU and Temeprature displays on the screen
- Set RGB patterns on the keyboard
- Set individual key colours

## Requirements

I am using poetry v1.7.1 to install the package

## Installation

You can install _Epomakercontroller_ via poetry

I suggest using conda or a python virtual env, tested on python 3.10 and 3.12:

```console
$ sudo apt install poetry
$ git clone https://github.com/strodgers/epomaker-controller
$ cd epomaker-controller
$ python3.10 -m venv venv
$ source venv/bin/activate
$ poetry install
```

## Usage

```console
$ epomakercontroller
Usage: epomakercontroller [OPTIONS] COMMAND [ARGS]...

  EpomakerController CLI.

Options:
  --help  Show this message and exit.

Commands:
  cycle-light-modes  Cycle through the light modes.
  list-temp-devices  List available temperature devices with detailed...
  send-cpu           Send CPU usage percentage to the Epomaker device.
  send-temperature   Send a temperature to the Epomaker device.
  send-time          Send the current time to the Epomaker device.
  set-rgb-all-keys   Set RGB colour for all keys.
  start-daemon       Start the CPU daemon to update the CPU usage.
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
