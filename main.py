import time
from temp.temperature import temperature

#Sensor-IDs
SENSOR_1 = "28-00000050b91c"
SENSOR_2 = "28-00000052834d"

HEATER_PIN = 5
SETPOINT = 30.0

def main():
    measure = temperature(SENSOR_1, SENSOR_2)
    temp1 = measure[0]
    temp2 = measure[1]
    print(f"Temperatur Sensor 1: {temp1:.2f} °C")
    print(f"Temperatur Sensor 2: {temp2:.2f} °C")

if __name__ == "__main__":
    main()