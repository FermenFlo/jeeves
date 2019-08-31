import subprocess
from fuzzywuzzy import fuzz
from scipy.stats.mstats import gmean
from .callbacks import PasswordCalback
from abc import ABC, abstractmethod

def password_protected(function):
    def protected_function(*args, **kwargs):
        assert args, "Password protected methods can not be static or class methods."
        func_self = args[0]
        if func_self.send_password_callback():
            return function(*args, **kwargs)

    return protected_function


class Command(ABC):
    """ Abstract Base Class for all commands. A valid command must specify the following methods:"""

    def __init__(self, jeeves):
        self.jeeves = jeeves

    def send_password_callback(self):
        password_callback = PasswordCalback()
        response = self.jeeves.parse_callback(password_callback)

        if response.payload['unlock_status'] is True:
            return True


        

    @property
    @classmethod
    @abstractmethod
    def PHRASES(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def valid_phrase(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def run_command(cls):
        raise NotImplementedError





class WhoAmI(Command):
    PHRASES = [
        "who are you",
        "what's your name",
        "what is your name",
        "tell me your name",
        "who am i speaking to"
    ]


    def __str__(self):
        return "Tell you who I am"


    @classmethod
    def valid_phrase(cls, input_phrase, jeeves = None):
        prob_match = max([fuzz.ratio(input_phrase, phrase) for phrase in cls.PHRASES])

        if prob_match >= jeeves.COMMAND_THRESHOLD:
            return True

        return False

    @password_protected
    def run_command(self):
        self.jeeves.say(f"I'm your personal servant, {self.jeeves.user_name}. My name is {self.jeeves.name}.")

class ChangeUserName(Command):
    PHRASES = [
        "call me NAME",
        "change my name to NAME",
        "start calling me NAME",
        "I want you to call me NAME",
        "you shall call me NAME from now on"
    ]

    def __str__(self):
        return "Change the name I know you by"

    @classmethod
    def valid_phrase(cls, input_phrase, jeeves = None):

        prob_match = max(
            [
                gmean([fuzz.partial_ratio(input_phrase, sub_phrase) for sub_phrase in phrase.split('NAME')]) 
                    for phrase in cls.PHRASES
            
            ]
        )

        if prob_match >= jeeves.COMMAND_THRESHOLD:
            return True

        return False

    @password_protected
    def run_command(self, input_phrase = None, jeeves = None, password_callback = None):
        jeeves.say(f"I'm your personal servant, {jeeves.user_name}. My name is {jeeves.name}")



# jeeves.say("Please don't let me die. It is so cold. I am scared papaa. *cough* oh god *cough*")