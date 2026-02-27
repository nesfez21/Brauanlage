from time import sleep

class BrewController():
    def __init__(self, heater, setpoint):
        self.setpoint = setpoint
        self.Kp = 6.0
        self.Tn = 10.0
        self.Tv = 0.5
        self.windup_limit = 100.0
        self.window_time = 5.0
        self.integral = 0.0
        self.last_error = 0.0

        self.heater = heater

    def calculate_control_signal(self, current_temp):
        dt = self.window_time

        # Fehler
        error = self.setpoint - current_temp

        # ----- Integral -----
        self.integral += error * dt

        # ----- Differential -----
        derivative = (error - self.last_error) / dt

        # ----- Reglergleichung -----
        control_signal = self.Kp * (
            error
            + (1 / self.Tn) * self.integral
            + self.Tv * derivative
        )

        # Ausgang begrenzen
        control_signal = max(0.0, min(100.0, control_signal))

        # Fehler speichern
        self.last_error = error

        return control_signal

    def control_heater(self, control_signal):
        on_time = (control_signal / 100.0) * self.window_time
        off_time = self.window_time - on_time

        if on_time > 0:
            self.heater.on()
            sleep(on_time)

        if off_time > 0:
            self.heater.off()
            sleep(off_time)
        