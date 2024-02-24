from datetime import datetime

# class EpomakerProfileCommand(EpomakerSimpleCommand):
#     """A command for setting the profile on the keyboard."""
#     class ProfileMode(Enum):
#         EPOMAKER_MODE_ALWAYS_ON                         = 0x01,
#         EPOMAKER_MODE_DYNAMIC_BREATHING                 = 0x02,
#         EPOMAKER_MODE_SPECTRUM_CYCLE                    = 0x03,
#         EPOMAKER_MODE_DRIFT                             = 0x04,
#         EPOMAKER_MODE_WAVES_RIPPLE                      = 0x05,
#         EPOMAKER_MODE_STARS_TWINKLE                     = 0x06,
#         EPOMAKER_MODE_STEADY_STREAM                     = 0x07,
#         EPOMAKER_MODE_SHADOWING                         = 0x08,
#         EPOMAKER_MODE_PEAKS_RISING_ONE_AFTER_ANOTHER    = 0x09,
#         EPOMAKER_MODE_SINE_WAVE                         = 0x0a,
#         EPOMAKER_MODE_CAISPRING_SURGING                 = 0x0b,
#         EPOMAKER_MODE_FLOWERS_BLOOMING                  = 0x0c,
#         EPOMAKER_MODE_LASER                             = 0x0e,
#         EPOMAKER_MODE_PEAK_TURN                         = 0x0f,
#         EPOMAKER_MODE_INCLINED_RAIN                     = 0x10,
#         EPOMAKER_MODE_SNOW                              = 0x11,
#         EPOMAKER_MODE_METEOR                            = 0x12,
#         EPOMAKER_MODE_THROUGH_THE_SNOW_NON_TRACE        = 0x13,
#         EPOMAKER_MODE_LIGHT_SHADOW                      = 0x15

#     def __init__(self, mode: ProfileMode, ) -> None:
#         initialization_data = bytearray.fromhex(
#             "07"
#             + f"{profile:02x}"
#             )
#         super().__init__(initialization_data

# test = EpomakerCommand(bytearray.fromhex("28000000000000d7"), packet_header_length=8, total_packets=1002)
# header_data = []
# for item in image_data_prefix:
#     header_data.append(bytearray.fromhex(item))
# test._insert_packet_headers(header_data)
