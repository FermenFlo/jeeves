from abc import ABC, abstractmethod
from .command_callbacks import PasswordCalback


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



