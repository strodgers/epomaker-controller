# Epomakercontroller

Some scripts to help interface with an Epomaker RT100 (will probably also work with TH80)

This project is still very rough around the edges

## Features

- Upload images to the RT100 screen
- Send arbitrary numbers to the CPU and Temeprature displays on the screen
- Set RGB patterns on the keyboard
- Set individual key colours

## Requirements

- See requirements.txt

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
$ epomakercontroller --help
Usage: epomakercontroller [OPTIONS] COMMAND [ARGS]...

  EpomakerController CLI.

Options:
  --help  Show this message and exit.

Commands:
  cycle-light-modes  Cycle through the light modes.
  send-cpu           Send the CPU usage percentage to the Epomaker device.
  send-temperature   Send the temperature to the Epomaker device.
  send-time          Send the current time to the Epomaker device.
  set-rgb-all-keys   Set RGB color for all keys.
  upload-image       Upload an image to the Epomaker device.
```

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
