import numpy as np
from abc import ABC, abstractmethod
from fuzzywuzzy import fuzz
from ..commands import Command


class State(ABC):

    def __init__(self, jeeves):
        self.jeeves = jeeves

    def listen(self, *args, **kwargs):
        return self.jeeves.listen(*args, **kwargs)

    @staticmethod
    def reset_state(jeeves):
        return Quiescent(jeeves)

    @classmethod
    @abstractmethod
    def run(cls):
        raise NotImplementedError


class Quiescent(State):

    @property
    def activated(self):
        phrase = self.listen()
        name_called_prob = max([fuzz.ratio(x, self.jeeves.name) for x in phrase.split()[:5]])
        if name_called_prob >= self.jeeves.NAME_THRESHOLD:
            self.jeeves.current_phrase = phrase
            return True

    def run(self):
        while True:
            if self.activated:
                return DecidingCommand(self.jeeves)


class DecidingCommand(State):

    DECIDING_MESSAGES = [
        "What would you like me to do?",
        "Can you repeat that?"

    ]

    num_retries = 0
    max_retries = 3

    # This state has a special init in which it loads all current commands
    def __init__(self, jeeves):
        super().__init__(jeeves)
        self.commands = self._load_commands()

    def _load_commands(self):
        return Command.__subclasses__()

    def match_commands(self, input_phrase):
        prob_matches = {cmd: cmd.prob_match(input_phrase) for cmd in self.commands}
        matches = [cmd for cmd, prob in prob_matches.items() if prob >= self.jeeves.COMMAND_THRESHOLD]

        return matches

    def handle_no_matches(self):
        while not self.matches and self.num_retries < self.max_retries:
            self.jeeves.say(np.random.choice(self.DECIDING_MESSAGES))
            retry_phrase = self.listen(60)
            self.matches = self.match_commands(retry_phrase)

        if not self.matches:  # give up
            return self.reset_state(self.jeeves)

    def handle_multiple_matches(self):
        options_string = f"Did you want me to: {' or '.join(self.matches)}"
        self.jeeves.say(options_string, wait=False)
        option_phrase = self.listen()

        match = max(self.matches, key=lambda x: fuzz.partial_ratio(option_phrase, x))

        self.matches = [match]

    def run(self):
        self.matches = self.match_commands(self.jeeves.current_phrase)

        if not self.matches:
            self.handle_no_matches()

        if len(self.matches) > 1:
            self.handle_multiple_matches()

        match = self.matches[0]
        return RunningCommand(self.jeeves, match)


class RunningCommand(State):

    # This state has a special init in which it accepts a command
    def __init__(self, jeeves, command):
        super().__init__(jeeves)

        self.command = command(jeeves)

    @property
    def command_is_running(self):
        try:
            return self.callback.status

        except AttributeError:
            return True

    def handle_password_callback(self, payload):
        if self.jeeves.password_unlocked:
            payload['unlock_status'] = True 

        input_password = self.listen(10)
        print(input_password)

        if any([fuzz.ratio(x, self.jeeves.PASSWORD) > self.jeeves.PASSWORD_THRESHOLD 
                for x in input_password.split()]):
            if np.random.random() < 0.05:
                self.jeeves.say("Lucky guess. I'm watching you", wait = False)

            self.jeeves.password_unlocked = True
            payload['unlock_status'] = True
            self.jeeves.say('Password verified.')

        else:
            self.callback.n_attempts -= 1
            n_attempts = self.callback.n_attempts
            self.jeeves.password_unlocked = False

            self.jeeves.say("Incorrect password!" + 
            f"{self.callback.n_attempts} attempts remain." if self.callback.n_attempts else "")

    def handle_input_callback(self, payload):
        for ask in payload['response_payload']:
            self.jeeves.say(ask, wait = False)
            response = self.listen(10)
            payload['response_payload'] = response

        return payload

    def handle_confirmation_callback(self, payload):
        for ask in payload['response_payload']:
            self.jeeves.say(ask, wait = False)
            response = self.listen(10)
            payload['response_payload'] = response

        return payload

    def parse_general_callback(self, callback):
        self.callback = callback
        status = callback.status
        callback_type = callback.callback_type
        payload = callback.response_payload

        # Success
        if status == 0:
            return self.reset_state(self.jeeves)


        # Error, just say you fucked up and return the reset state
        if status == 2:
            self.jeeves.say()
            return self.reset_state(self.jeeves)

        # Pending, reuires user input
        if status == 1:
            handling_func_name = f"handle_{callback_type}_callback"
            handling_func = getattr(self, handling_func_name)
            self.callback.payload = handling_func(payload)
            
            return self.callback

    def run(self):
        while self.command_is_running:
            self.parse_general_callback(self.command.run(self.jeeves))

        return Quiescent(self.jeeves)