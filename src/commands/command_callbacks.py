# Password Unlock
# * First asks Jeeves if it is unlocked
# * Otherwise, requests password input from user
from abc import ABC, abstractmethod


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
    def payload(cls):
        return {}


class SuccessCallback(Callback):
    """ The success callback is a simple callback that lets Jeeves know that the command has terminated
    in a graceful manner and that it can return to its quiescent state. """

    status = 0
    callback_type = "success"
    payload = {}


class ErrorCallback(Callback):
    """ The error callback lets Jeeves know that the command terminated in an unsuccessful state. However,
    Jeeves still returns to its quiescent state after receving this callback. """

    status = 2
    callback_type = "error"
    payload = {}


class PasswordCalback(Callback):
    """ The password callback requests a password unlock from Jeeves. Jeeves, after recognizing this
    callback will check its internal password state. A successful will change the response payload value
    to True and result in an unlock that lasts for 5 minutes for the current user. Otherwise, the payload
    value will remain False and Jeeves will remain password-protected. """

    def __init__(self, payload={"unlock_status": False}):
        self.payload = payload

    status = 1
    callback_type = "password"
    payload = {}

class InputCallback(Callback):
    """ The input callback is special in that it allows further user input. The response payload is
    keyed by phrases which Jeeves will ask the user. The response will be stored in the value for the
    corresponding key. e.g.:
                payload = {'What would you like your new name to be?': ''}

    will get turnd into:
                payload = {'What would you like your new name to be?': 'Eliza'}

    after Jeeves asks the user: 'What would you like your new name to be?' and they respond with 'Eliza'
    """

    def __init__(self, payload={"": ""}):
        self.payload = payload

    status = 1
    callback_type = "input"
    payload = {}


class ConfirmationCallback(Callback):
    """ The confirmation callback simply asks Jeeves to receive confirmation from the user via speech.
    You can think of it as a special case of the Input callback -a close cousin. However, in the case of
    the confirmation callback, the values in the response payload are booleans which Jeeves interprets
    from inputs such as 'yes', 'no', 'yeah', 'nope', etc... """

    def __init__(self, payload={"Are you sure?": False}):
        self.payload = payload

    status = 1
    callback_type = "confirmation"
    payload = {}
