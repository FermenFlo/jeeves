import speech_recognition as sr
import subprocess
import numpy as np
import os
import arrow
from wit import Wit
from jeeves.src.states.states import Quiescent, RunningCommand
from jeeves.src.commands import Command  # grab all commands that are subclasses of the Command ABC


class Jeeves:
    """ Jeeves """

    DEFAULT_USER_NAME = "brian"
    DEFAULT_NAME = "alex"
    PASSWORD = "what are you gay"

    NAME_THRESHOLD = 75
    COMMAND_THRESHOLD = 60
    PASSWORD_THRESHOLD = 95

    FALLBACK_MESSAGES = [
        "I'm sorry, I didn't quite catch that. Maybe try annunciating for once in your god damn life",
        "What?",
        "bruh, speak up",
        "sorry, I don't speak italian.",
        "aaaaaaaaa I'm awake. I totally wasn't sleeping.",
    ]

    def __init__(self):
        self.state = Quiescent(self)
        self._user_name = self.DEFAULT_USER_NAME
        self._name = self.DEFAULT_NAME

        self._last_password_unlock_time = arrow.Arrow(1, 1, 1)  # long time ago

        self.commands = self._load_commands()
        self.current_phrase = ""

        self.FALLBACK_MESSAGES += [f"you should speak up, {self.user_name}"]
        self._awakeners = []  # TODO Make this read from a config

    def _load_commands(self):
        return Command.__subclasses__()

    @property
    def awakeners(self):
        return self._awakeners

    @awakeners.setter
    def awakeners(self, input_list):
        self._awakeners = sorted(input_list, key=lambda x: x.awaken_time)

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, input_name):
        self._user_name = input_name.lower()

    @property
    def password_unlocked(self):
        now = arrow.utcnow()
        time_since_last_unlock = (now - self._last_password_unlock_time).seconds

        if time_since_last_unlock <= 300:  # 5 minute lockout time
            return True

        return False

    @password_unlocked.setter
    def password_unlocked(self, input_value):
        if input_value is True:
            self._last_password_unlock_time = arrow.utcnow()

        else:
            self._last_password_unlock_time = arrow.Arrow(1, 1, 1)  # minimum value for arrow package

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, input_name):
        self._name = input_name.lower()

    @property
    def active_command(self):
        if isinstance(self.state, RunningCommand):
            return self.state.command

    def listen(self, n_seconds=None):
        """ Standard method to listening for requests. Doesn't require activation phrase.
        Limit input windows with n_seconds. """
        arrow_max = arrow.Arrow(9999, 12, 31, 23, 59, 59, 999999)  # arrow's max
        next_awaken_time = self.awakeners[0].awaken_time if self.awakeners else arrow_max
        requested_end_time = arrow.utcnow().shift(seconds=n_seconds) if n_seconds else arrow_max

        actual_end_time = min(next_awaken_time, requested_end_time)
        while arrow.utcnow() <= actual_end_time:
            # TODO
            if self.awakeners:
                continue
            try:
                # with sr.WavFile("/Users/brian/code/jeeves/timer_test.wav") as source:
                with self.mic as source:
                    self.r.adjust_for_ambient_noise(source)
                    audio = self.r.listen(source)
                    phrase = self.r.recognize_google(audio).lower()
                    return phrase

            except sr.UnknownValueError:
                continue

        return ""  # Didn't get any input

    def say(self, text=None, wait=True):
        """ Speaks """
        text = text or np.random.choice(self.FALLBACK_MESSAGES)

        # Wait for subprocess to complete or not
        if wait:
            subprocess.call(["say", text, "-v", self.DEFAULT_NAME])
        else:
            subprocess.Popen(["say", text, "-v", self.DEFAULT_NAME])

    def start(self):
        """ Starts Jeeves """
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()
        self.wit = Wit(os.environ["WIT_ACCESS_TOKEN"])

        while True:
            print(self.state)
            self.state = self.state.run()
