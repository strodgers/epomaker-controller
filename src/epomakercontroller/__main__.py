"""Command-line interface."""

import click
from epomakercontroller import *


@click.command()
@click.version_option()
def main() -> None:
    """Epomakercontroller."""


if __name__ == "__main__":
    main(prog_name="EpomakerController")  # pragma: no cover
