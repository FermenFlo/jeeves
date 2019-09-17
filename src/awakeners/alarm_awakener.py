from jeeves.src.awakeners import Awakener
from jeeves.src.commands.Alarm.activate_alarm import ActivateAlarm


class AlarmAwakener(Awakener):
    def run_command(self, jeeves):
        from jeeves.src.states.states import RunningCommand

        return RunningCommand(jeeves, ActivateAlarm)
