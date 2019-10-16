from jeeves.src.awakeners.alarm_awakener import AlarmAwakener
from jeeves.src.commands.callbacks import SuccessCallback
from jeeves.src.commands.commands import Command
import arrow
from dateutil import tz


class SetAlarm(Command):
    INTENT_VALUE = "set_alarm"

    def __str__(self):
        return "Set a timer."

    @staticmethod
    def parse_datetime_response(datetime_dict):
        response_type = datetime_dict["type"]

        if response_type == "value":
            response_time = datetime_dict["value"]

        elif response_type == "interval":
            response_time = datetime_dict["to"]["value"]

        provided_time = arrow.get(response_time)
        tz_provided_time = provided_time.to(tz.tzlocal())
        return tz_provided_time

    @staticmethod
    def parse_duration_response(datetime_dict):
        seconds_duration = datetime_dict["normalized"]["value"]
        provided_time = arrow.utcnow().shift(seconds=seconds_duration)
        tz_provided_time = provided_time.to(tz.tzlocal())

        return tz_provided_time

    def run(self, jeeves):
        entities = self.jeeves.wit_response["entities"]

        sorted_datetimes = (
            sorted(entities["datetime"], key=lambda x: -x["confidence"]) if "datetime" in entities else []
        )
        sorted_durations = (
            sorted(entities["duration"], key=lambda x: -x["confidence"]) if "duration" in entities else []
        )

        max_datetime_confidence = sorted_datetimes[0]["confidence"] if sorted_datetimes else 0
        max_duration_confidence = sorted_durations[0]["confidence"] if sorted_durations else 0

        if max_datetime_confidence >= max_duration_confidence:
            provided_time = self.parse_datetime_response(sorted_datetimes[0])

        else:
            provided_time = self.parse_duration_response(sorted_durations[0])

        awakener = AlarmAwakener(provided_time)
        self.jeeves.awakeners.append(awakener)

        if arrow.utcnow() > provided_time:
            # Easter egg
            self.jeeves.say(f"Okay, I'll build a time machine and then alert you {provided_time.humanize()}")

        else:
            self.jeeves.say(f"Okay, I'll alert you {provided_time.humanize()}")

        return SuccessCallback()
