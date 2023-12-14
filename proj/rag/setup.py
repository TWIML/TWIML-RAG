import os
import argparse

from typing import Literal

# TODO: run a quick search on all uses of os.getenv to see what varnames are used
# and make sure you are accounting for all of them, and changing their instantiation
# if you change the name used for them etc.

# TODO: complete the below (types for env-var names, cli-prompter w. file-write & argparser etc.)

RequiredKeys = Literal[
    ''
]

class CliPrompter:
    pass