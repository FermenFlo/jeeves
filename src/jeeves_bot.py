import speech_recognition as sr
import subprocess
import numpy as np
import os
import arrow
from wit import Wit
import asyncio
from jeeves.src.states.states import Quiescent
from jeeves.src.commands import Command  # grab all commands that are subclasses of the Command ABC
import asyncio


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
        "aaaaaaaaa I'm awake. I totally wasn't sleeping.",
    ]

    def __init__(self):
        self.state = Quiescent(self)
        self._user_name = self.DEFAULT_USER_NAME
        self._name = self.DEFAULT_NAME

        self._last_password_unlock_time = arrow.Arrow(1, 1, 1)  # long time ago

        self.commands = self._load_commands()
        self.current_phrase = asyncio.Future()

        self.FALLBACK_MESSAGES += [f"you should speak up, {self.user_name}"]
        self.awakeners = []  # TODO Make this read from a config

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

    def listening_callback(self, recognizer, audio):

        try:
            if not self.phrase.done():
                phrase = r.recognize_google(audio).lower()
                self.phrase.set_result(phrase)

        except sr.UnknownValueError:
            pass

    async def listen(self, n_seconds=None):
        """ Standard method to listening for requests. Doesn't require activation phrase.
        Limit input window with n_seconds. """
        self.phrase = asyncio.Future()  # should always be a string prior to this point
        end_time = (
            arrow.utcnow().shift(seconds=n_seconds) if n_seconds else arrow.Arrow(9999, 12, 31, 23, 59, 59, 999999)
        )  # arrow's max

        while not self.phrase.done() and arrow.utcnow() <= end_time:
            with mic as source:
                r.adjust_for_ambient_noise(source)
                # with sr.WavFile("/Users/brian/code/jeeves/timer_test.wav") as source:

            # returns a callable which will terminate the extra thread for listening
            stop_listening = r.listen_in_background(mic, self.callback)

            try:
                await asyncio.wait_for(self.phrase, n_secs)
                break

            except TimeoutError:  # thrown by asyncio.wait_for
                break

        stop_listening()
        self.phrase = self.phrase.result() if self.phrase.done() else ""

        return self.phrase

    async def check_awakeners(self):
        while not self.activated:  # while not activated
            for i in range(len(self.awakeners)):
                self.awakeners[i] += 1

                # if isinstance(self.phrase, asyncio.Future):
            await asyncio.sleep(1)

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
        self.wit = Wit(os.environ["WIT_ACCESS_TOKEN"])

        while True:
            print(self.state)
            self.state = self.state.run()
