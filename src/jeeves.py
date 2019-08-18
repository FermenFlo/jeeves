import speech_recognition as sr
from fuzzywuzzy import fuzz
import subprocess
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .commands import Command  # grab all command that are subclasses of the Command ABC

class Jeeves:
    """ Jeeves """
    
    DEFAULT_USER_NAME = 'brian'
    DEFAULT_NAME = 'servant'
    PASSWORD = 'apple'
    
    NAME_THRESHOLD = 75
    COMMAND_THRESHOLD = 60
    PASSWORD_THRESHOLD = 95

    FALLBACK_MESSAGES = [
        "I'm sorry, I didn't quite catch that. Maybe try annunciating for once in your god damn life",
        "What?",
        "bruh, speak up",
        "sorry, I don't speak italian.",
        f"you should speak up, {DEFAULT_USER_NAME}",
        "aaaaaaaaa I'm awake. I totally wasn't sleeping."
    ]


    def __init__(self):
        self._user_name = self.DEFAULT_USER_NAME
        self._name = self.DEFAULT_NAME

        self._last_password_unlock_time = datetime(2000, 1, 1)  # long time ago

        self.commands = self._load_commands()

    def _load_commands(self):
        return Command.__subclasses__()

    @property
    def user_name(self):
        return self._user_name

    @property
    def password_unlocked(self):
        now = datetime.utcnow()
        time_since_last_unlock = (now - self._last_password_unlock_time).seconds

        if time_since_last_unlock <=  300:  # 5 minute lockout time
            return True

        return False

    @password_unlocked.setter
    def password_unlocked(self, input_value):
        if input_value == True:
            self._last_password_unlock_time = datetime.utcnow()

        else:
            self._last_password_unlock_time = datetime(2000, 1, 1)

    @user_name.setter
    def user_name(self, input_name):
        self._user_name = input_name.lower()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, input_name):
        self._name = input_name.lower()

    @property
    def activated(self):
        try:
            with self.mic as source:
                self.r.adjust_for_ambient_noise(source)

                audio = self.r.listen(source)
                phrase = self.r.recognize_google(audio).lower()
                
                
                name_called_prob = max([fuzz.ratio(x, self.name) for x in phrase.split()[:5]])
                if name_called_prob >= self.NAME_THRESHOLD:
                    self.current_phrase = phrase
                    return True 

        except sr.UnknownValueError:
            return False

    def listen(self, n_seconds = None):
        """ Standard method to listening for requests. Doesn't require activation phrase. 
        Limit input windows with n_seconds. """
        end_time = (datetime.utcnow() + relativedelta(seconds = n_seconds)) if n_seconds else datetime.max

        while datetime.utcnow() <= end_time:
            try:
                with self.mic as source:
                    self.r.adjust_for_ambient_noise(source)
                    audio = self.r.listen(source)
                    phrase = self.r.recognize_google(audio).lower()
                    return phrase

            except sr.UnknownValueError:
                continue

        return '' # Didn't get any input


    def start(self):
        """ Starts Jeeves """
        self.r = sr.Recognizer()
        self.mic = sr.Microphone()

        while True:
            if self.activated:
                self.take_command()

    def take_command(self):
        valid_commands = [cmd for cmd in self.commands if cmd.valid_phrase(self.current_phrase, jeeves = self)]
        valid_commands = sorted(valid_commands, reverse = True)

        if len(valid_commands) >= 1:
            command = valid_commands[0]
            command.run_command(input_phrase = self.current_phrase, jeeves = self, password_callback = self.password_request)

        # elif:  # Write logic to allow user to pick 1 of the matching commands 
        #     print('TODO')
        #     pass

        else:  # couldn't understand user
            self.say(np.random.choice(self.FALLBACK_MESSAGES))

        
    def password_request(self):
        if self.password_unlocked:
            return True

        self.say('This is a protected command. What is the password?')
        input_password = self.listen(n_seconds = 60)

        if fuzz.ratio(input_password, self.PASSWORD) > self.PASSWORD_THRESHOLD:
            if np.random.random() > .95:
                self.say("Lucky guess. I'm watching you")

            self.password_unlocked = True
            return True

        else:
            self.say("INTRUDER! INTRUDER!")
            self.password_unlocked = True

    def say(self, text):
        """ Speaks """
        subprocess.call(['say', text])