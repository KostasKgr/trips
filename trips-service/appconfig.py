import os
from distutils.util import strtobool

class Config(object):
    SIMULATION_DELAY_SECONDS_MINIMUM = float(
        os.environ.get("SIMULATION_DELAY_SECONDS_MINIMUM", "0.5"))

    SIMULATION_DELAY_SECONDS_MAXIMUM = float(
        os.environ.get("SIMULATION_DELAY_SECONDS_MAXIMUM", "1.5"))
