"""CHOSEN world parameters, not fitted measurements."""
from math import pi

WINDOW_MS = 50.0
EAR_BIN_MS = 5.0
ARENA_MM = 40.0
INITIAL_DISTANCE_MM = 6.0
INITIAL_HALF_ANGLE = pi / 6
CONTACT_MM = 2.0
SCENT_D0_MM = 5.0
SMELL_MAX_HZ = 180.0
CONTACT_MAX_HZ = 180.0
EYE_MAX_HZ = 180.0
HORIZONTAL_FOV = 300.0
VERTICAL_FOV = 210.0
BODY_WIDTH_MM = 1.0
BODY_HEIGHT_MM = 2.0
CONTRAST = 1.0
MOTOR_SCALE_HZ = 450.0
MAX_TURN_RAD_S = pi
MAX_FORWARD_MM_S = 10.0
MAX_REVERSE_MM_S = 5.0
PULSE_GROUP = "ps1_MN"
SINE_GROUP = "i1_MN"
CONTACT_GROUP = "ppk23"


def chosen():
    return {k: v for k, v in globals().items() if k.isupper()}
