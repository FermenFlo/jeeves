from abc import ABC, abstractmethod
from fuzzywuzzy import fuzz


class State(ABC):

    def __init__(self, jeeves):
        self.jeeves = jeeves

    def listen(self, *args, **kwargs):
        self.jeeves.listen(*args, **kwargs)

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
            self.jeeves.activation_phrase = phrase
            return True

    def run(self):
        while True:
            if self.activated:
                return DecidingCommand(self.jeeves)


class DecidingCommand(State):

    num_retries = 0
    max_retries = 3

    # This state has a special init in which it loads all current commands
    def __init__(self):
        super().__init__()
        self.commands = self._load_commands()

    def _load_commands(self):
        return Command.__subclasses__()

    def match_commands(self, input_phrase):
        prob_matches = {cmd: cmd.valid_phrase(input_phrase) for cmd in self.commands}
        matches = [cmd for cmd, prob in prob_matches.items() if prob >= self.jeeves.COMMAND_THRESHOLD]

        return matches

    def handle_no_matches(self):
        while not self.matches and self.num_retries < self.max_retries:
            self.jeeves.say()
            retry_phrase = self.listed(60)
            self.matches = self.match_commands(retry_phrase)

        if not self.matches:  # give up
            return self.reset_state(self.jeeves)

    def handle_multiple_matches(self):
        options_string = f"Did you want me to: {" or ".join(self.matches)}"
        self.jeeves.say(options_string, wait=False)
        option_phrase = listen()

        match = max(self.matches, key=lambda x: fuzz.partial_ratio(option_phrase, x))

        self.matches = [match]

    def run_command(self):
        matched_command = self.matches[0]
        return RunningCommand(self.jeeves, matched_command)

    def run(self):
        self.matches = self.match_commands(self.jeeves.current_phrase)

        if not self.matches:
            self.handle_no_matches()

        if len(self.matches) > 1:
            self.handle_multiple_matches()

        else:
            self.run_command()


class RunningCommand(State):

    # This state has a special init in which it accepts a command
    def __init__(self, command):
        super().__init__()
        self.command = command(self.jeeves)

    @property
    def command_is_running(self):
        self.callback['status'] if self.callback else True

    def handle_password_callback(self, payload):
         if self.jeeves.password_unlocked:
            payload['unlock_status'] = True

        self.jeeves.say("This is a protected command. What is the password?")
        input_password = self.listen(60)

        if fuzz.ratio(input_password, self.jeeves.PASSWORD) > self.jeeves.PASSWORD_THRESHOLD:
            if np.random.random() < 0.05:
                self.say("Lucky guess. I'm watching you", wait = False)

            self.jeeves.password_unlocked = True

            payload['unlock_status'] = True

        else:
            self.say("INTRUDER! INTRUDER!")
            self.jeeves.password_unlocked = False

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
        status = callback['status']
        callback_type = callback['callback_type']
        payload = callback['response_payload']

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
            payload = handling_func(payload)

            return payload

    def run(self):
        while self.command_is_running:
            self.parse_general_callback(self.command.run())