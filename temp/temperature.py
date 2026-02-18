from temp.read_temperature import temp_read

def temperature(sensor_id_1, sensor_id_2):
    temp_1 = temp_read(sensor_id_1)
    if temp_1 is None:
        print("Temperatur von Sensor 1 konnte nicht gelesen werden")

    temp_2 = temp_read(sensor_id_2)
    if temp_2 is None:
        print("Temperatur von Sensor 2 konnte nicht gelesen werden")

    avg_temp = (temp_1 + temp_2) / 2

    return temp_1, temp_2, avg_temp