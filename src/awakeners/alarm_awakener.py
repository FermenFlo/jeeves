from jeeves.src.awakeners import Awakener
from jeeves.src.commands.Alarm.activate_alarm import ActivateAlarm
from jeeves.src.states import RunningCommand


class AlarmAwakener(Awakener):
    def run_command(self, jeeves):

        return RunningCommand(jeeves, ActivateAlarm)
