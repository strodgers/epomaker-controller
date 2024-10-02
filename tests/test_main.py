"""Test cases for the __main__ module."""

import pytest
from click.testing import CliRunner
from typing import Iterator, Iterable
from epomakercontroller.commands.data.constants import (
    IMAGE_DIMENSIONS,
    Profile,
)
from epomakercontroller.commands import (
    EpomakerImageCommand,
    EpomakerKeyRGBCommand,
    EpomakerProfileCommand,
)
from epomakercontroller.commands.reports import Report
import random
import numpy as np
import matplotlib.pyplot as plt  # type: ignore
import cv2

from epomakercontroller.configs.configs import ConfigType, get_all_configs
from epomakercontroller.utils.keyboard_keys import KeyboardKeys

# Set to True to display images
DISPLAY = False

CONFIGS = get_all_configs()


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces.

    Returns:
        CliRunner: The Click CLI runner.
    """
    return CliRunner()


class DataHelper:
    """Test data for the EpomakerController."""

    def __init__(self, test_name: str) -> None:
        """Initializes the DataHelper object.

        Args:
            test_name (str): The name of the test.

        Raises:
            ValueError: If the test data file cannot be read.
        """
        self.name = test_name
        test_file = f"tests/data/{test_name}.txt"
        self.command_data = []
        with open(test_file, "r") as file:
            # Ignore the first line
            file.readline()
            try:
                self.command_data = [
                    bytes.fromhex(line.strip()) for line in file.readlines()
                ]
            except ValueError as e:
                print(f"Error reading test data {test_file}: {e}")
                raise e
        assert len(self.command_data) > 0

    def __iter__(self) -> Iterator[bytes]:
        """Iterates over the command data.

        Yields:
            Iterator[bytes]: The command data.
        """
        for data in self.command_data:
            yield data

    def __getitem__(self, index: int) -> bytes:
        """Gets a command data byte by index.

        Args:
            index (int): The index of the command data byte.

        Returns:
            bytes: The command data byte.
        """
        return self.command_data[index]


all_tests = [
    "EpomakerImageCommand-upload-calibration-image",
    "EpomakerImageCommand-upload-red-image",
    "EpomakerKeyRGBCommand-all-keys-set",
    "EpomakerKeyRGBCommand-all-keys-unique",
    "EpomakerKeyRGBCommand-multiple-keys",
    "EpomakerKeyRGBCommand-single-key",
    "EpomakerKeyRGBCommand-numrow-keys-different-frames",
    "EpomakerCommand-cycle-light-modes-command",
    "_decode_rgb565-calibration-image-bytes",
]

all_test_data = {test: DataHelper(test) for test in all_tests}


def assert_colour_close(
    original: tuple[int, int, int],
    decoded: tuple[int, int, int],
    delta: int = 8,
    debug_str: str = "",
) -> None:
    """Asserts that two colours are within an acceptable delta of each other.

    This is necessary because the RGB565 encoding and decoding process is lossy.

    Args:
        original (tuple[int, int, int]): The original colour.
        decoded (tuple[int, int, int]): The decoded colour.
        delta (int): The acceptable difference. Defaults to 8.
        debug_str (str): The debug string. Defaults to "".
    """
    for o, d in zip(original, decoded, strict=True):
        assert (
            abs(o - d) <= delta
        ), f"{debug_str} Original: {original}, Decoded: {decoded}, Delta: {delta}"


def pair_bytes(data: bytes) -> list[bytes]:
    """Combine bytes into 2 bytes.

    Args:
        data (bytes): The data to combine.

    Returns:
        list[bytes]: The combined bytes.
    """
    assert len(data) % 2 == 0, "Data must be of even length"
    return [data[i : i + 2] for i in range(0, len(data), 2)]


def test_encode_decode_rgb565() -> None:
    """Test the _encode_rgb565 and _decode_rgb565 functions."""
    # Test data
    rgb = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Encode and decode
    encoded = EpomakerImageCommand.EpomakerImageCommand._encode_rgb565(*rgb)
    decoded = EpomakerImageCommand.EpomakerImageCommand._decode_rgb565(encoded)

    assert_colour_close(rgb, decoded)


def test_read_and_decode_bytes() -> None:
    """Test reading bytes from a text file and decoding them."""
    this_test_data = all_test_data["_decode_rgb565-calibration-image-bytes"]
    pixel_pairs = []
    for pair in [pair_bytes(data) for data in this_test_data]:
        pixel_pairs += pair

    # Decode the pixel pairs
    pixels = []
    for pixel in pixel_pairs:
        pixels += list(
            EpomakerImageCommand.EpomakerImageCommand._decode_rgb565(
                int.from_bytes(pixel, byteorder="big")
            )
        )

    # Remove padding bytes from the end of the image
    pixels = pixels[: IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1] * 3]

    # Convert the pixel data to an 8-bit image
    test_image_8bit = np.array(pixels, dtype=np.uint8).reshape(
        (IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1], 3)
    )

    # Check similarity
    image_path = "tests/data/calibration.png"
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, IMAGE_DIMENSIONS)
    image = cv2.flip(image, 0)
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    similarity = cv2.matchTemplate(image, test_image_8bit, cv2.TM_CCOEFF_NORMED)
    min_val, *_ = cv2.minMaxLoc(similarity)

    assert min_val > 0.99

    # Display the images
    if DISPLAY:
        plt.subplot(1, 2, 1)
        plt.imshow(image)
        plt.title("Original Image")
        plt.axis("off")  # Hide the axes

        plt.subplot(1, 2, 2)
        plt.imshow(test_image_8bit)
        plt.title("Test Image")
        plt.axis("off")  # Hide the axes

        plt.show()
    pass


def byte_wise_difference(bytes1: bytes, bytes2: bytes) -> list[int]:
    """Calculate byte-wise difference between two bytes objects.

    Args:
        bytes1 (bytes): The first bytes object.
        bytes2 (bytes): The second bytes object.

    Raises:
        ValueError: If the bytes objects are of different lengths.

    Returns:
        list[int]: The list of differences.
    """
    # Ensure the bytes objects are of the same length
    if len(bytes1) != len(bytes2):
        raise ValueError("Bytes objects must be of the same length")

    # Calculate the byte-wise difference
    differences = [abs(b1 - b2) for b1, b2 in zip(bytes1, bytes2, strict=True)]

    return differences


def test_encode_image_command() -> None:
    """Test encoding an image command."""
    command = EpomakerImageCommand.EpomakerImageCommand()
    this_test_data = all_test_data["EpomakerImageCommand-upload-calibration-image"]
    command.encode_image("tests/data/calibration.png")

    # Initial report should always be equal
    assert command.reports[0].report_bytearray == this_test_data.command_data[0]

    i = 0
    for t, d in zip(this_test_data, command, strict=True):
        if i == 0:
            i += 1
            continue

        difference = byte_wise_difference(t, d[:])

        # Headers should always be equal
        assert (
            t[: command.report_data_header_length]
            == d[: command.report_data_header_length]
        )

        # Iterate over byte pairs and assert the colour difference
        j = 0
        for d_colour, t_colour in zip(
            d[command.report_data_header_length :],
            t[command.report_data_header_length :],
            strict=True,
        ):
            # Convert byte pair to integer
            # Assert the colour difference
            if d_colour != t_colour:
                assert_colour_close(
                    EpomakerImageCommand.EpomakerImageCommand._decode_rgb565(d_colour),
                    EpomakerImageCommand.EpomakerImageCommand._decode_rgb565(t_colour),
                    debug_str=f"Packet {i}, Pair {j} ",
                )

            j += 1

        assert np.all(np.array(difference) <= 8)
        i += 1


def test_checksum() -> None:
    """Test checksum calculation for reports."""
    # Some commands use the 8th bit as the checksum
    this_test_data = all_test_data["EpomakerCommand-cycle-light-modes-command"]
    checkbit = 8
    for i, t in enumerate(this_test_data):
        checksum = Report.Report._calculate_checksum(t[:checkbit])
        assert checksum == t[checkbit].to_bytes(
            1, byteorder="big"
        ), f"""{i} > Checksum: {checksum!r},
        Buffer: {hex(t[checkbit])},
        test {this_test_data.name}"""

    # Some commands use the 7th bit as the checksum
    checkbit = 7
    for this_test_data in [
        all_test_data["EpomakerImageCommand-upload-calibration-image"],
        all_test_data["EpomakerKeyRGBCommand-all-keys-set"],
        all_test_data["EpomakerKeyRGBCommand-all-keys-unique"],
        all_test_data["EpomakerKeyRGBCommand-single-key"],
    ]:
        for i, t in enumerate(this_test_data):
            checksum = Report.Report._calculate_checksum(t[:checkbit])
            assert checksum == t[checkbit].to_bytes(1, byteorder="big"), (
                f"{i} > Checksum: {checksum!r},"
                "Buffer: {hex(t[checkbit])},"
                "test {this_test_data.name}"
            )


def compare_bytes_iterable(a: Iterable[bytes], b: Iterable[bytes]) -> None:
    """Compare two iterables of bytes.

    Args:
        a (Iterable[bytes]): The first iterable.
        b (Iterable[bytes]): The second iterable.
    """
    for i, (t, d) in enumerate(zip(a, b, strict=True)):
        if t != d:
            for j, (x, y) in enumerate(zip(t, d, strict=True)):
                assert x == y, f"Byte in row {i}, position {j}: {x:02x} != {y:02x}"


def test_set_rgb_all_keys() -> None:
    """Test setting RGB values for all keys."""
    this_test_data = all_test_data["EpomakerKeyRGBCommand-all-keys-set"]
    keyboard_keys = KeyboardKeys(CONFIGS[ConfigType.CONF_KEYMAP])
    mapping = EpomakerKeyRGBCommand.KeyMap(keyboard_keys)
    for key in keyboard_keys:
        mapping[key] = (100, 5, 69)
    frames = [EpomakerKeyRGBCommand.KeyboardRGBFrame(key_map=mapping, time_ms=50)]
    command = EpomakerKeyRGBCommand.EpomakerKeyRGBCommand(frames)

    compare_bytes_iterable(this_test_data, command.iter_report_bytes())


def test_set_rgb_multiple_frames() -> None:
    """Test setting RGB values for multiple frames."""

    # This test is expecting the number row numbers to each be set in a different frame

    this_test_data = all_test_data["EpomakerKeyRGBCommand-numrow-keys-different-frames"]
    frames = []
    keyboard_keys = KeyboardKeys(CONFIGS[ConfigType.CONF_KEYMAP])

    # frames 1 to 9 each set NUMROW_1 to NUMROW_9
    for i in range(1, 10):
        mapping = EpomakerKeyRGBCommand.KeyMap(keyboard_keys)
        key = keyboard_keys.get_key_by_name(f"NUMROW_{i}")
        assert key is not None, "Failed to get key by name"
        mapping[key] = (255, 255, 255)
        frames.append(
            EpomakerKeyRGBCommand.KeyboardRGBFrame(key_map=mapping, time_ms=i * 10, index=i - 1)
        )

    # frame 10 has NUMROW_0 set
    mapping = EpomakerKeyRGBCommand.KeyMap(keyboard_keys)
    key = keyboard_keys.get_key_by_name("NUMROW_0")
    assert key is not None, "Failed to get key by name"
    mapping[key] = (255, 255, 255)
    frames.append(EpomakerKeyRGBCommand.KeyboardRGBFrame(key_map=mapping, time_ms=100, index=9))

    command = EpomakerKeyRGBCommand.EpomakerKeyRGBCommand(frames)
    compare_bytes_iterable(this_test_data, command.iter_report_bytes())


def test_set_light_mode() -> None:
    """Test setting the light mode."""
    this_test_data = all_test_data["EpomakerCommand-cycle-light-modes-command"]
    profile = Profile(
        mode=Profile.Mode.ALWAYS_ON,
        speed=Profile.Speed.DEFAULT,
        brightness=Profile.Brightness.DEFAULT,
        dazzle=Profile.Dazzle.OFF,
        option=Profile.Option.OFF,
        rgb=(180, 180, 180),
    )
    command = EpomakerProfileCommand.EpomakerProfileCommand(profile)
    assert this_test_data[0] == command.reports[0].report_bytearray

    # TODO: there are loads of other light modes to test
