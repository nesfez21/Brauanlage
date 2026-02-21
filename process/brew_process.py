import time


class BrewProcess:

    def __init__(self, preheat_controller, brew_controller):

        self.preheat_controller = preheat_controller
        self.brew_controller = brew_controller

        self.active_controller = None

        self.state = "IDLE"

        self.current_temp = 0.0
        self.setpoint = 0.0

        self.preheat_setpoint = 0.0

        self.mash_profile = []
        self.current_step = 0
        self.step_start_time = None

        self.message = ""

    # --------------------------------------------------
    # VORHEIZEN STARTEN
    # --------------------------------------------------

    def start_preheat(self, setpoint):
        self.preheat_setpoint = setpoint
        self.setpoint = setpoint

        self.active_controller = self.preheat_controller

        self.state = "PREHEATING"
        self.message = "Vorheizen gestartet"

    # --------------------------------------------------
    # MAISCHPROFIL LADEN
    # mash_profile = [{"temp": 63, "time": 30}, ...]
    # --------------------------------------------------

    def load_mash_profile(self, profile):
        self.mash_profile = profile

    # --------------------------------------------------
    # MAISCHEN STARTEN (nach PREHEAT_READY)
    # --------------------------------------------------

    def start_mash(self):

        if self.state != "PREHEAT_READY":
            return

        if not self.mash_profile:
            self.message = "Kein Maischprofil geladen"
            return

        self.current_step = 0
        self.step_start_time = None

        self.active_controller = self.brew_controller
        self.setpoint = self.mash_profile[0]["temp"]

        self.state = "MASHING"
        self.message = "Maischprofil gestartet"

    # --------------------------------------------------
    # ZYKLISCHES UPDATE (jede Sekunde aufrufen)
    # --------------------------------------------------

    def update(self, temperature):

        self.current_temp = temperature

        # ---------------------------------------------
        # PREHEATING
        # ---------------------------------------------

        if self.state == "PREHEATING":

            control = self.active_controller.calculate_control_signal(
                self.current_temp
            )
            self.active_controller.control_heater(control)

            if self.current_temp >= self.preheat_setpoint:
                self.state = "PREHEAT_READY"
                self.message = "Vorheizen fertig – Maische einfüllen"

        # ---------------------------------------------
        # PREHEAT_READY (halten!)
        # ---------------------------------------------

        elif self.state == "PREHEAT_READY":

            control = self.active_controller.calculate_control_signal(
                self.current_temp
            )
            self.active_controller.control_heater(control)

        # ---------------------------------------------
        # MASHING
        # ---------------------------------------------

        elif self.state == "MASHING":

            step = self.mash_profile[self.current_step]
            self.setpoint = step["temp"]

            control = self.active_controller.calculate_control_signal(
                self.current_temp
            )
            self.active_controller.control_heater(control)

            # Wenn Temperatur erreicht → Zeit starten
            if self.current_temp >= self.setpoint:

                if self.step_start_time is None:
                    self.step_start_time = time.time()
                    self.message = f"Rast {self.current_step + 1} gestartet"

                else:
                    elapsed = time.time() - self.step_start_time

                    if elapsed >= step["time"] * 60:
                        self._next_step()

        # ---------------------------------------------
        # FINISHED
        # ---------------------------------------------

        elif self.state == "FINISHED":
            self.active_controller.control_heater(0)

    # --------------------------------------------------
    # NÄCHSTE RAST
    # --------------------------------------------------

    def _next_step(self):

        self.current_step += 1
        self.step_start_time = None

        if self.current_step >= len(self.mash_profile):
            self.state = "FINISHED"
            self.message = "Maischprofil abgeschlossen"
        else:
            self.setpoint = self.mash_profile[self.current_step]["temp"]
            self.message = f"Wechsel zu Rast {self.current_step + 1}"

    # --------------------------------------------------
    # STATUS FÜR FLASK
    # --------------------------------------------------

    def get_status(self):

        return {
            "state": self.state,
            "temperature": round(self.current_temp, 2),
            "setpoint": self.setpoint,
            "step": self.current_step + 1 if self.mash_profile else 0,
            "message": self.message
        }