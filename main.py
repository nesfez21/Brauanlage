import time
from temp.temperature import temperature
from controller.controller_preheat import PreheatController

#Sensor-IDs
SENSOR_1 = "28-00000050b91c"
SENSOR_2 = "28-00000052834d"

HEATER_PIN = 5
SETPOINT = 45.0

def main():
    preheat_controller = PreheatController(HEATER_PIN, SETPOINT)

    while True:
        measure = temperature(SENSOR_1, SENSOR_2)
        temp1 = measure[0]
        temp2 = measure[1]
        avg_temp = measure[2]
        
        print(f"Temperatur Sensor 1: {temp1:.2f} °C")
        print(f"Temperatur Sensor 2: {temp2:.2f} °C")

        control_signal = preheat_controller.calculate_control_signal(temp2)
        print(f"Heizleistung: {control_signal:.2f} %")
        preheat_controller.control_heater(control_signal)

if __name__ == "__main__":
    main()