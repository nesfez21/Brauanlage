from time import sleep

class BoilController:

    def __init__(self, heater):
        self.heater = heater

    def control(self, current_temp):

        if current_temp < 98:
            power = 100
        else:
            power = 70  # stabile Kochleistung

        return power

    def apply(self, power):

        window_time = 5.0
        on_time = (power / 100) * window_time
        off_time = window_time - on_time

        if on_time > 0:
            self.heater.on()
            sleep(on_time)

        if off_time > 0:
            self.heater.off()
            sleep(off_time)