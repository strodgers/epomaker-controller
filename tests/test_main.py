"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from epomakercontroller import __main__
from epomakercontroller.epomakercontroller import EpomakerController, IMAGE_DIMENSIONS
from epomakercontroller.data.command_data import image_data_prefix
import random
import numpy as np
import matplotlib.pyplot as plt
import cv2
import math

@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


def assert_colour_close(original: tuple[int, int, int], decoded: tuple[int, int, int], delta: int = 8) -> None:
    """Asserts that two colors are within an acceptable delta of each other.
    This is necessary because the RGB565 encoding and decoding process is lossy.
    """
    for o, d in zip(original, decoded):
        assert abs(o - d) <= delta, f"Original: {original}, Decoded: {decoded}, Delta: {delta}"


def test_encode_decode_rgb565() -> None:
    """Test the _encode_rgb565 and _decode_rgb565 functions."""
    # Test data
    red = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    green = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    blue = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Encode and decode
    encoded_red = EpomakerController._encode_rgb565(*red)
    decoded_red = EpomakerController._decode_rgb565(encoded_red)
    encoded_green = EpomakerController._encode_rgb565(*green)
    decoded_green = EpomakerController._decode_rgb565(encoded_green)
    encoded_blue = EpomakerController._encode_rgb565(*blue)
    decoded_blue = EpomakerController._decode_rgb565(encoded_blue)

    assert_colour_close(red, decoded_red)
    assert_colour_close(green, decoded_green)
    assert_colour_close(blue, decoded_blue)


def test_read_and_decode_bytes() -> None:
    """Test reading bytes from a text file and decoding them."""
    # Test data
    # file_path = "tests/data/upload-calibration-image-bytes.txt"
    file_path = "/home/sam/Documents/keyboard-usb-sniff/EpomakerController/EpomakerController/image_data.txt"

    # Read bytes from file
    with open(file_path, "r") as file:
        hex_data_full = file.readlines()

    # Parse the hex data assuming a 2-byte color encoding (16 bits per pixel)
    pixels = []
    for line in hex_data_full:
        # Each pair of values now represents one pixel
        if ":" in line:
            pixel_values = line.strip().split(':')
        else:
            pixel_values = [line[i:i+2] for i in range(0, len(line), 2)]
        for i in range(0, len(pixel_values), 2):
            try:
                # Convert every 2 values into a single integer representing a pixel
                pixel = int("".join(pixel_values[i:i+2]), 16)
                pixels.append(pixel)
            except ValueError:
                # In case of incomplete values, we break the loop
                break

    shape = IMAGE_DIMENSIONS
    num_pixels = shape[0] * shape[1]
    image_data = pixels[:num_pixels]  # Ensure we only take the number of pixels we need
    image_array_16bit = np.array(image_data, dtype=np.uint16).reshape(shape)

    rgb_array_decoded = np.array(
        [EpomakerController._decode_rgb565(pixel) for pixel in image_array_16bit.ravel()],
        dtype=np.uint8
        )
    rgb_image = rgb_array_decoded.reshape((shape[0], shape[1], 3))

    # Display the RGB image
    plt.imshow(rgb_image)
    plt.axis('off')  # Hide the axes
    plt.show()
    # Assertions
    # assert isinstance(decoded_text, str)
    # assert len(decoded_text) > 0
    # assert decoded_text.startswith("Hello")
    # assert decoded_text.endswith("world!")


def test_encode_image() -> None:
    image_path = "tests/data/calibration.png"
    image = cv2.imread(image_path)
    image = cv2.resize(image, IMAGE_DIMENSIONS)
    image = cv2.flip(image, 0)
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    image_16bit = np.zeros((IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]), dtype=np.uint16)
    try:
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                r, g, b = image[y, x]
                image_16bit[y, x] = EpomakerController._encode_rgb565(r, g, b)
    except Exception as e:
        print(f"Exception while converting image: {e}")

    image_data = ""
    for row in image_16bit:
        image_data += ''.join([hex(val)[2:].zfill(4) for val in row])

    # 4 bytes per pixel (16 bits)
    assert len(image_data) == (IMAGE_DIMENSIONS[0] * IMAGE_DIMENSIONS[1]) * 4
    buffer_length = 128 - len(image_data_prefix[0])
    with open("image_data.txt", "w", encoding="utf-8") as file:
        chunks = math.floor(len(image_data) / buffer_length)
        i = 0
        while i < chunks:
            image_byte_segment = image_data[i*buffer_length:(i+1)*buffer_length]
            file.write(f"{image_byte_segment}\n")
            i += 1
        # Remainder of the data
        image_byte_segment = EpomakerController._pad_command(
            image_data[i*buffer_length:], buffer_length
            )
        file.write(f"{image_byte_segment}\n")

def test_send_imagfe() -> None:
    controller = EpomakerController()
    controller.send_image("/home/sam/Documents/keyboard-usb-sniff/EpomakerController/EpomakerController/tests/data/calibration.png")
    pass
