import numpy as np
import os
from jeeves.src.commands import InternalCommand
from jeeves.src.commands.callbacks import SuccessCallback
from dateutil.relativedelta import relativedelta
from datetime import datetime
import subprocess


class ActivateAlarm(InternalCommand):
    def __init__(self, jeeves, length=5):
        super().__init__(jeeves)
        self.length = length

    @property
    def alarm_file(self):
        root_dir = "/System/Library/Sounds/"
        files = os.listdir(root_dir)
        chosen_file = os.path.join(root_dir, np.random.choice(files))

        return chosen_file

    def run(self, jeeves):
        stop_time = datetime.utcnow() + relativedelta(seconds=self.length)

        while datetime.utcnow() <= stop_time:
            subprocess.call(["afplay", self.alarm_file])

        self.jeeves.say("Your timer has expired.")
        return SuccessCallback()
