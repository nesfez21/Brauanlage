import time


class BrewProcess:
    def __init__(self):
        self.mash_profile = []
        self.current_step_index = 0
        self.step_start_time = None

    def load_recipe(self, recipe):
        self.mash_profile = recipe["mash_profile"]
        self.current_step_index = 0
        self.step_start_time = None

    def get_first_temp(self):
        if not self.mash_profile:
            return None
        return self.mash_profile[0]["temp"]

    def get_profile(self):
        return self.mash_profile

    def update(self, current_temp):
        if self.current_step_index >= len(self.mash_profile):
            return None

        step = self.mash_profile[self.current_step_index]
        target = step["temp"]

        if current_temp >= target - 1.0:

            if self.step_start_time is None:
                self.step_start_time = time.time()

            elapsed = time.time() - self.step_start_time

            if elapsed >= step["time"] * 60:

                self.current_step_index += 1
                self.step_start_time = None

                if self.current_step_index < len(self.mash_profile):
                    return self.mash_profile[self.current_step_index]["temp"]
                else:
                    return None

        return target

    def get_remaining_time(self):

        if self.step_start_time is None:
            return None

        step = self.mash_profile[self.current_step_index]
        total_time = step["time"] * 60

        elapsed = time.time() - self.step_start_time
        remaining = total_time - elapsed

        return max(0, int(remaining))