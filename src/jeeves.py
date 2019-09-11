import speech_recognition as sr
from fuzzywuzzy import fuzz
import subprocess
import numpy as np
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from wit import Wit
from .states import Quiescent, RunningCommand
from .commands import Command  # grab all commands that are subclasses of the Command ABC


class Jeeves:
    """ Jeeves """

    DEFAULT_USER_NAME = "brian"
    DEFAULT_NAME = "samantha"
    PASSWORD = "turtle"

    NAME_THRESHOLD = 75
    COMMAND_THRESHOLD = 60
    PASSWORD_THRESHOLD = 95

    FALLBACK_MESSAGES = [
        "I'm sorry, I didn't quite catch that. Maybe try annunciating for once in your god damn life",
        "What?",
        "bruh, speak up",
        "sorry, I don't speak italian.",
        f"you should speak up, {DEFAULT_USER_NAME}",
        "aaaaaaaaa I'm awake. I totally wasn't sleeping.",
    ]

    def __init__(self):
        self.state = Quiescent(self)
        self._user_name = self.DEFAULT_USER_NAME
        self._name = self.DEFAULT_NAME

        self._last_password_unlock_time = datetime.min  # long time ago

        self.commands = self._load_commands()
        self.current_phrase = ""

        self.FALLBACK_MESSAGES = [
        "I'm sorry, I didn't quite catch that. Maybe try annunciating for once in your god damn life",
        "What?",
        "bruh, speak up",
        "sorry, I don't speak italian.",
        f"you should speak up, {self.user_name}",
        "aaaaaaaaa I'm awake. I totally wasn't sleeping.",
    ]

    def _load_commands(self):
        return Command.__subclasses__()

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, input_name):
        self._user_name = input_name.lower()

    @property
    def password_unlocked(self):
        now = datetime.utcnow()
        time_since_last_unlock = (now - self._last_password_unlock_time).seconds
        print(self._last_password_unlock_time)
        print(now)

        if time_since_last_unlock <= 300:  # 5 minute lockout time
            return True

        return False

    @password_unlocked.setter
    def password_unlocked(self, input_value):
        if input_value is True:
            self._last_password_unlock_time = datetime.utcnow()

        else:
            self._last_password_unlock_time = datetime.min

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
        end_time = (datetime.utcnow() + relativedelta(seconds=n_seconds)) if n_seconds else datetime.max

        while datetime.utcnow() <= end_time:
            try:
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
            subprocess.call(["say", text])
        else:
            subprocess.Popen(["say", text])

    def start(self):
        """ Starts Jeeves """
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()
        self.wit = Wit(os.environ['WIT_ACCESS_TOKEN'])
        
        while True:
            print(self.state)
            self.state = self.state.run()
