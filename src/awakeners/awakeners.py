from datetime import datetime
from abc import ABC, abstractmethod

class Awakener(ABC):
    """Awakeners are a simple way of getting around complex multithreading with Jeeves. For instance, to achieve
    setting a timer, you can create an awakener, an object which when activated comes with instructions for jeeves
    to execute at that given time. In this case the instructions would be to play an alarm. This what, the main thread
    can simply check the status of all awakeners every second or so, avoiding clogging up the main thread.
    
    Awakeners have a run_command method which bypasses Jeeves' DecidingCommand state and immediately runs the provided
    with the provided settings.
    
    NOTE: Awakeners are jeeves-agnostic and simply rely on time-based activations. """

    def __init__(self, awaken_time):
        self.awaken_time = awaken_time

    @property
    def activated(self):
        if datetime.utcnow() >= self.awaken_time:
            return True
        
        return False

    @classmethod
    @abstractmethod
    def run_command(cls, jeeves):
        raise NotImplementedError