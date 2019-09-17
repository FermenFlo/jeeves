from jeeves.src.awakeners.alarm_awakener import AlarmAwakener
from jeeves.src.commands.callbacks import SuccessCallback
from jeeves.src.commands.commands import Command
from dateutil import parser
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SetAlarm(Command):
    INTENT_VALUE = "set_alarm"

    def __str__(self):
        return "Set a timer."

    @staticmethod
    def parse_datetime_response(datetime_dict):
        response_type = datetime_dict["type"]

        if response_type == "value":
            response_time = datetime_dict["value"]
            provided_time = parser.parse(response_time, ignoretz=True)

            return provided_time

        if response_type == "interval":
            response_time = datetime_dict["to"]
            provided_time = parser.parse(response_time, ignoretz=True)

            return provided_time

    @staticmethod
    def parse_duration_response(datetime_dict):
        seconds_duration = datetime_dict["normalized"]["value"]
        provided_time = datetime.utcnow() + relativedelta(seconds=seconds_duration)

        return provided_time

    def run(self, jeeves):
        entities = self.jeeves.wit_response["entities"]

        sorted_datetimes = (
            sorted(entities["datetime"], key=lambda x: -x["confidence"]) if "datetime" in entities else []
        )
        sorted_durations = (
            sorted(entities["duration"], key=lambda x: -x["confidence"]) if "durations" in entities else []
        )

        max_datetime_confidence = sorted_datetimes[0]["confidence"] if sorted_datetimes else 0
        max_duration_confidence = sorted_durations[0]["confidence"] if sorted_durations else 0

        if max_datetime_confidence >= max_duration_confidence:
            provided_time = self.parse_datetime_response(sorted_datetimes[0])

        else:
            provided_time = self.parse_duration_response(sorted_durations[0])

        awakener = AlarmAwakener(provided_time)
        self.jeeves.awakeners.append(awakener)

        return SuccessCallback()
