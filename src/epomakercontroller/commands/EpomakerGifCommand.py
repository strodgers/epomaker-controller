"""Command for sending animated GIFs natively to the Epomaker keyboard.

The keyboard firmware supports multi-frame image uploads. The protocol is:
- 1 init report: specifies frame count, per-frame data size, frame delay, and dimensions
- For each frame: 1000 data reports (type 0x38) + 1 footer report (type 0x34)
- Frame numbers are 1-based in data report headers

Init header byte layout (12 bytes), confirmed via USB sniffing:
  [0]     0xa5            Command ID (image upload)
  [1]     0x00            Sub-command
  [2]     uint8           Frame count (e.g. 0x12 = 18 frames; 0x01 for static)
  [3]     uint8           Frame delay in ms (e.g. 0x42 = 66ms; 0x00 for static)
  [4-5]   LE16            Per-frame data size (0xDAF4 = 56052 = 162*173*2 for full-res)
  [6]     0x00            Reserved
  [7]     checksum        0xFF - (sum(bytes[0:7]) & 0xFF)
  [8-11]  varies          Unknown trailing bytes (static: 00 00 a2 ad)

  Example (sniffed GIF):  a5 00 12 42 68 2e 00 70 0f 40 93 6d
  Example (static image): a5 00 01 00 f4 da 00 8b 00 00 a2 ad

Data report header (8 bytes):
  [0]     0x25            Report type
  [1]     0x00            Sub-type
  [2]     uint8           Frame number (1-based)
  [3]     0x00            Reserved
  [4-5]   LE16            Sequence number within frame (0-based)
  [6]     0x38/0x34       0x38 = data, 0x34 = last report of frame
  [7]     checksum
  [8-63]  56 bytes        Pixel data (RGB565)
"""
from __future__ import annotations

import math
import os
from typing import TYPE_CHECKING, override

import cv2
import numpy as np

if TYPE_CHECKING:
    from PIL import Image

from .EpomakerCommand import EpomakerCommand, CommandStructure, EpomakerStreamedCommand, IEpomakerCommand
from .data.constants import IMAGE_DIMENSIONS
from .reports.Report import Report, BUFF_LENGTH
from .reports.ReportWithData import ReportWithData
from .utils import image_utils
from ..logger.logger import Logger


class EpomakerGifCommand(EpomakerStreamedCommand):
    """A command for sending animated GIFs natively to the keyboard."""

    FRAMERATE = 15

    @staticmethod
    def best_gif_dimensions(source_width: int, source_height: int) -> tuple[int, int]:
        """Find the largest 4K-aligned dimensions that fit the screen and
        best match the source GIF's aspect ratio.

        Args:
            source_width: Original GIF width in pix els.
            source_height: Original GIF height in pixels.

        Returns:
            (width, height) tuple for the GIF upload.
        """
        compress_ratio = \
            min(
                IMAGE_DIMENSIONS[0] / source_width,
                IMAGE_DIMENSIONS[1] / source_height,
            )

        source_width = math.ceil(source_width * compress_ratio)
        source_height = math.ceil(source_height * compress_ratio)

        return math.floor(source_width / 64) * 64, math.floor(source_height / 64) * 64

    def __init__(self, gif_path: str) -> None:
        prepared_data = self.prepare_gif(gif_path)

        if not all(prepared_data):
            return

        self.gif, self.n_frames, self.step, self.gif_dimensions = prepared_data
        self.frame_delay_ms = frame_delay_ms = int(1000 / self.FRAMERATE * self.step)
        self.report_data_header_length = 8

        gif_dimensions = self.gif_dimensions

        # Raw pixel data per frame MUST be a multiple of 4096.
        # The firmware's animation framebuffer uses 4K page alignment;
        # non-aligned sizes cause vertical line artifacts.
        raw_per_frame = gif_dimensions[0] * gif_dimensions[1] * 2
        if raw_per_frame % 4096 != 0:
            raise ValueError(
                f"GIF dimensions {gif_dimensions} produce per_frame_size="
                f"{raw_per_frame} which is not a multiple of 4096. "
                f"Choose dimensions where w*h*2 % 4096 == 0."
            )

        self.raw_per_frame = raw_per_frame

        data_payload = BUFF_LENGTH - 8  # 56 bytes
        self.per_frame_size = raw_per_frame
        self.reports_per_frame = math.ceil(raw_per_frame / data_payload)
        self.data_reports_per_frame = self.reports_per_frame - 1

        self.data_buff_length = BUFF_LENGTH - self.report_data_header_length  # 56
        self.global_report_idx = 1  # init report is index 0
        self.encoded = 0
        self.composited_frames = None

        total_reports = self.n_frames * self.reports_per_frame
        structure = CommandStructure(
            number_of_starter_reports=1,
            number_of_data_reports=total_reports,
            number_of_footer_reports=0,
        )

        init_hex = self._build_init_header(self.n_frames, frame_delay_ms,
                                            self.per_frame_size, gif_dimensions)
        initial_report = Report(init_hex, index=0, checksum_index=None)
        super().__init__(initial_report, structure)

    @staticmethod
    def prepare_gif(gif_path: str):
        if not os.path.isfile(gif_path):
            Logger.log_error(f"Could not find GIF: {gif_path}")
            return None, None, None

        try:
            from PIL import Image as PILImage

            gif = PILImage.open(gif_path)
        except ImportError:
            Logger.log_error("GIF upload requires Pillow: install python-pillow or Pillow")
            return None, None, None
        except Exception as e:
            Logger.log_error(f"Failed to open GIF: {e}")
            return None, None, None

        n_frames_actual = getattr(gif, 'n_frames', 1)
        n_frames = min(n_frames_actual, 56)
        step = n_frames_actual / n_frames

        gif_dimensions = EpomakerGifCommand.best_gif_dimensions(*gif.size)
        Logger.log_info(f"New GIF size if {gif_dimensions}")
        return gif, n_frames, step, gif_dimensions

    @staticmethod
    def _build_init_header(n_frames: int, delay_ms: int,
                           per_frame_size: int,
                           gif_dimensions: tuple[int, int]) -> str:
        """Build the init report header hex string.

        Args:
            n_frames (int): Number of frames (max 255).
            delay_ms (int): Frame delay in milliseconds (max 255).
            per_frame_size (int): Bytes per frame.
            gif_dimensions (tuple): (width, height) of GIF frames.

        Returns:
            str: Hex string for the init report.
        """
        header_before_checksum = bytearray([
            0xa5, 0x00,
            n_frames & 0xFF,
            min(delay_ms, 255) & 0xFF,
            per_frame_size & 0xFF,
            (per_frame_size >> 8) & 0xFF,
            0x00,
        ])
        checksum = (0xFF - (sum(header_before_checksum) & 0xFF)) & 0xFF
        w, h = gif_dimensions
        full_header = header_before_checksum + bytearray([
            checksum,
            0x00, 0x00,
            w & 0xFF, h & 0xFF,
        ])
        return full_header.hex()

    @staticmethod
    def _prepare_frame_image(pil_frame: Image.Image,
                             dimensions: tuple[int, int]) -> np.ndarray:
        """Convert a PIL Image frame to a flattened RGB565 8-bit numpy array.

        Args:
            pil_frame (Image.Image): A PIL RGB image.
            dimensions (tuple): (width, height) to resize to.

        Returns:
            np.ndarray: Flattened uint8 array of RGB565 data.
        """
        rgb_array = np.array(pil_frame)
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

        image = cv2.resize(bgr_array, dimensions)
        image = cv2.flip(image, 0)
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_16bit = np.zeros(
            (image.shape[0], image.shape[1]), dtype=np.uint16
        )
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                r, g, b = image[y, x]
                image_16bit[y, x] = image_utils.encode_rgb565(r, g, b)

        return np.ndarray.flatten(IEpomakerCommand._np16_to_np8(image_16bit))

    def _extract_composited_frames(self, gif: Image.Image) -> list[Image.Image]:
        """Extract all frames from a GIF with proper compositing.

        Optimized GIFs use partial/diff frames where only changed pixels are
        stored, with transparency for unchanged areas. We must composite each
        frame onto a canvas to produce complete images, respecting disposal
        methods.

        Args:
            gif (Image.Image): An opened PIL GIF image.

        Returns:
            list[Image.Image]: List of fully composited RGB frames.
        """
        step = self.step

        from PIL import Image as PILImage

        canvas = PILImage.new("RGBA", gif.size, (0, 0, 0, 255))
        frames: list[Image.Image] = []

        for i in range(self.n_frames):
            gif.seek(int(i * step))
            frame_rgba = gif.convert("RGBA")

            canvas.paste(frame_rgba, (0, 0), frame_rgba)
            frames.append(canvas.copy().convert("RGB"))

            disposal = gif.disposal_method if hasattr(gif, 'disposal_method') else 0
            if disposal == 2:
                canvas = PILImage.new("RGBA", gif.size, (0, 0, 0, 255))

        return frames

    @override
    def _generate_chunk(self):
        data_buff_length = self.data_buff_length
        global_report_id = self.global_report_idx

        for frame_id, pil_frame in enumerate(self.composited_frames):
            try:
                raw_bytes = self._prepare_frame_image(
                    pil_frame, self.gif_dimensions
                ).tobytes()

                frame_bytes = raw_bytes
            except Exception as e:
                Logger.log_error(f"Exception encoding frame {frame_id}: {e}")
                return

            frame_number = frame_id + 1  # 1-based
            data_pointer = 0

            for seq in range(self.data_reports_per_frame):
                seq_bytes = seq.to_bytes(2, "big")
                report = ReportWithData(
                    header_format_string=(
                        "2500{frame:02x}00"
                        "{seq_upper:02x}{seq_lower:02x}38"
                    ),
                    index=global_report_id,
                    header_format_values={
                        "frame": frame_number,
                        "seq_upper": seq_bytes[1],
                        "seq_lower": seq_bytes[0],
                    },
                    checksum_index=7,
                )
                chunk = frame_bytes[data_pointer:data_pointer + data_buff_length]
                report.add_data(chunk)
                data_pointer += data_buff_length
                yield report

            footer_seq = self.data_reports_per_frame
            footer_seq_bytes = footer_seq.to_bytes(2, "big")
            footer_report = ReportWithData(
                header_format_string=(
                    "2500{frame:02x}00"
                    "{seq_upper:02x}{seq_lower:02x}34"
                ),
                index=global_report_id + 1,
                header_format_values={
                    "frame": frame_number,
                    "seq_upper": footer_seq_bytes[1],
                    "seq_lower": footer_seq_bytes[0],
                },
                checksum_index=7,
            )
            remaining = frame_bytes[data_pointer:]

            padded = bytes(remaining) + b'\x00' * (data_buff_length - len(remaining))
            footer_report.add_data(padded)
            yield footer_report

            self.global_report_idx += 2
            Logger.log_info(f"Encoded frame {frame_id + 1}/{self.n_frames}")

    def encode_gif(self) -> bool:
        """Encode all GIF frames using per-frame report structure.

        Each frame is encoded identically to a static image upload:
        1000 data reports (type 0x38, seq 0-999) + 1 footer report
        (type 0x34, seq 1000). Frame number increments per frame (1-based).
        This exactly matches the proven working static image protocol.
        """
        gif = self.gif
        if not gif:
            Logger.log_error("Failed to encode GIF data")
            return False

        self.composited_frames = self._extract_composited_frames(gif)
        Logger.log_info(f"Extracted {len(self.composited_frames)} composited frames")
        return True
