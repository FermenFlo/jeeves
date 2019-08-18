from abc import ABC
import abc


class Command(ABC):
    """ Abstract Base Class for all commands. A valid command must specify the following methods:"""

    def __init__(self):
        pass

    @property
    @abc.abstractmethod
    def PHRASES(self):
        raise NotImplementedError

    @abc.abstractmethod
    def valid_phrase(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_command(self):
        raise NotImplementedError
