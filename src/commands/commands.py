import subprocess
from fuzzywuzzy import fuzz
from scipy.stats.mstats import gmean
from abc import ABC, abstractmethod
from .callbacks import *

def password_protected(function):
    def protected_function(*args, **kwargs):
        assert len(args), "Password protected methods can not be static or class methods."
        func_self = args[0]
        if func_self.send_password_callback():
            return function(*args, **kwargs)
        
        else:
            pass

    return protected_function

class Command(ABC):
    """ Abstract Base Class for all commands. A valid command must specify the following methods:"""

    def __init__(self, jeeves):
        self.jeeves = jeeves

    def send_password_callback(self):
        if self.jeeves.password_unlocked is True:
            return True

        self.jeeves.say("This is a protected command. What is the password?")
        
        cb =  PasswordCallback()
        while cb.n_attempts > 0 and not cb.response_payload['unlock_status']:
            cb = self.jeeves.state.parse_general_callback(cb)

        return cb.response_payload['unlock_status']

    @classmethod
    def prob_match(cls, input_phrase):
        prob_match = max([fuzz.ratio(input_phrase, phrase) for phrase in cls.PHRASES])

        return prob_match

    @property
    @classmethod
    @abstractmethod
    def PHRASES(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def run(cls):
        raise NotImplementedError

class WhoAmI(Command):
    PHRASES = ["who are you", "what's your name", "what is your name", 
    "tell me your name", "who am i speaking to", "tell me who you are"]

    def __str__(self):
        return "Tell you who I am"

    @password_protected
    def run(self, jeeves):
        jeeves.say(f"I'm your personal servant {jeeves.user_name}. My name is {jeeves.name}.")
        return SuccessCallback()



class ChangeUserName(Command):
    PHRASES = [
        "call me NAME",
        "change my name to NAME",
        "start calling me NAME",
        "I want you to call me NAME",
        "you shall call me NAME from now on",
    ]

    def __str__(self):
        return "Change the name I know you by"

    @classmethod
    def valid_phrase(cls, input_phrase, jeeves=None):

        prob_match = max(
            [
                gmean([fuzz.partial_ratio(input_phrase, sub_phrase) for sub_phrase in phrase.split("NAME")])
                for phrase in cls.PHRASES
            ]
        )

        if prob_match >= jeeves.COMMAND_THRESHOLD:
            return True

        return False

    @staticmethod
    @password_protected
    def run(input_phrase=None, jeeves=None, password_callback=None):
        jeeves.say(f"I'm your personal servant, {jeeves.user_name}. My name is {jeeves.name}")


# jeeves.say("Please don't let me die. It is so cold. I am scared papaa. *cough* oh god *cough*")

