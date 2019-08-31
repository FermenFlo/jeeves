import subprocess
from fuzzywuzzy import fuzz
from .base_commands import Command
from scipy.stats.mstats import gmean


def password_protected(function):
    def protected_function(*args, **kwargs):
        if kwargs["password_callback"]():
            function(*args, **kwargs)

    return protected_function

def password_protected(function):
    def protected_function(*args, **kwargs):
        assert args, "Password protected methods can not be static or class methods."
        func_self = args[0]
        if func_self.send_password_callback():
            return function(*args, **kwargs)

    return protected_function


class WhoAmI(Command):
    PHRASES = ["who are you", "what's your name", "what is your name", "tell me your name", "who am i speaking to"]

    def __str__(self):
        return "Tell you who I am"

    @staticmethod
    @password_protected
    def run_command(input_phrase=None, jeeves=None, password_callback=None):
        jeeves.say(f"I'm your personal servant, {jeeves.user_name}. My name is {jeeves.name}.")


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
    def run_command(input_phrase=None, jeeves=None, password_callback=None):
        jeeves.say(f"I'm your personal servant, {jeeves.user_name}. My name is {jeeves.name}")


# jeeves.say("Please don't let me die. It is so cold. I am scared papaa. *cough* oh god *cough*")

