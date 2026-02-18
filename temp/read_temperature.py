def temp_read(sensor_id):
    path = f"/sys/bus/w1/devices/{sensor_id}/w1_slave"      #Pfad der Sensor-Datei

    with open(path, 'r') as file:       #Öffnet Datei, with schließt Datei automatisch, r für read
        lines = file.readlines()

    if "YES" not in lines[0]:       #Messung erfolgreich?
        return None

    temp_value = lines[1].split("t=")[1]      #Extrahiert Temperaturwert, 2. Zeile der Datei, trennt bei "t=" und nimmt rechten Teil
    temp = float(temp_value) / 1000.0      #WMilligrad zu Grad, float
    
    return temp