from gpiozero import OutputDevice
from time import sleep

class PreheatController():
    def __init__(self, heater_pin, setpoint):
        self.setpoint = setpoint
        self.Kp = 5.5
        self.Ki = 0.01
        self.windup_limit = 100.0
        self.window_time = 5.0

        self.heater = OutputDevice(heater_pin)
        self.integral = 0.0
        self.integral_zone = 1.5

    def calculate_control_signal(self, current_temp):
        error = self.setpoint - current_temp
        dt = self.window_time

        if 0 < error < self.integral_zone:
            # normal aufbauen
            self.integral += error * dt * self.Ki

        elif error < 0:
            # langsamer abbauen (z. B. 20 % Geschwindigkeit)
            self.integral += error * dt * self.Ki * 0.2

        self.integral = max(0.0, min(100.0, self.integral))

        control_signal = self.Kp * error + self.integral
        # Begrenzen auf 0–100 %
        control_signal = max(0, min(100, control_signal))

        print(f"Error: {error:.2f}, Integral: {self.integral:.2f}")

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
        