from abc import ABC, abstractmethod
from fuzzywuzzy import fuzz
from .command_callbacks import PasswordCallback

class Command(ABC):
    """ Abstract Base Class for all commands. A valid command must specify the following methods:"""

    def __init__(self, jeeves):
        self.jeeves = jeeves

    def send_password_callback(self):
        return PasswordCallback()

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
    def valid_phrase(cls):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def run_command(cls):
        raise NotImplementedError


class Callback(ABC):
    """ Abstract Base Class for all callbacks. A valid callback must specify the following methods:"""

    def __init__(self, response_payload={}):
        self.reponse_payload = response_payload

    @property
    @classmethod
    @abstractmethod
    def status(cls):
        """ Status lets Jeeves know whaat needs to happen next in terms of state and control flow.
        The following are defined statuses:

        0: Success; causes Jeeves to break out of command and return to queiescent state
        1: Pending; causes Jeeves to something (or nothing) and return the callback to the command
        2: Error; causes Jeeves to break out of command and return to queiescent state
        """
        raise NotImplementedError

    @property
    @classmethod
    @abstractmethod
    def callback_type(cls):
        return ""

    @property
    @classmethod
    @abstractmethod
    def response_payload(cls):
        return {}
