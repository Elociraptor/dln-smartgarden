# =====================================================
# IMPORT SECTION
# =====================================================

# System Imports
import time
import gc
from machine import ADC, Pin

# Sensor Imports
import dht
import machine
from hcsr04 import HCSR04

from mysettings import (
    # Hardware Pins
    DHT22PIN,
    ULTRASONIC_TRIGGER_PIN,
    ULTRASONIC_ECHO_PIN,
    ULTRASONIC_TIMEOUT_US,
    MOISTURE_SENSOR_PIN,
    
    # ADC Einstellungen
    ADC_WIDTH,
    ADC_ATTENUATION,
    
    # Timing
    MESSAGE_INTERVAL,
    
    # MQTT Topics
    TEMP_TOPIC,
    HUMI_TOPIC,
    DIST_TOPIC,
    MOIST_TOPIC,
    
    # System Einstellungen
    DEBUG_MODE,
    MEMORY_MONITORING,
    
    # Sensor Limits
    TEMP_MIN_LIMIT,
    TEMP_MAX_LIMIT,
    HUMI_MIN_LIMIT,
    HUMI_MAX_LIMIT,
    DIST_MIN_LIMIT,
    DIST_MAX_LIMIT,
    SENSOR_RETRY_COUNT,
    
    # Feuchtigkeits-Schwellwerte
    MOISTURE_DRY_THRESHOLD,
    MOISTURE_WET_THRESHOLD,
    
    # Fehler-Nachrichten
    ERROR_MSG_TEMP,
    ERROR_MSG_HUMI,
    ERROR_MSG_DIST,
    ERROR_MSG_MOIST,
    
    # Backwards Compatibility
    message_interval
)

# =====================================================
# SENSOR INITIALISIERUNG
# =====================================================

def init_sensors():
    """
    Initialisiert alle Sensoren mit Parametern aus mysettings.py
    Returns: Dictionary mit Sensor-Objekten
    """
    if DEBUG_MODE:
        print('\n=== SENSOR INITIALISIERUNG ===')
    
    sensors = {}
    
    try:
        # ===== DHT22 =====
        if DEBUG_MODE:
            print('Initialisiere DHT22 Sensor (Pin {})...'.format(DHT22PIN))
        sensors['dht'] = dht.DHT22(machine.Pin(DHT22PIN))
        
        # ===== HC-SR04 =====
        if DEBUG_MODE:
            print('Initialisiere HC-SR04 (Trigger: {}, Echo: {})...'.format(
                ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN))
        sensors['ultrasonic'] = HCSR04(
            trigger_pin=ULTRASONIC_TRIGGER_PIN,
            echo_pin=ULTRASONIC_ECHO_PIN,
            echo_timeout_us=ULTRASONIC_TIMEOUT_US
        )
        
        # ===== BODENFEUCHTIGKEITSSENSOR =====
        if DEBUG_MODE:
            print('Initialisiere Bodenfeuchtigkeitssensor (Pin {})...'.format(MOISTURE_SENSOR_PIN))
        
        moisture_adc = ADC(Pin(MOISTURE_SENSOR_PIN))
        moisture_adc.width(ADC_WIDTH)
        moisture_adc.atten(ADC_ATTENUATION)
        sensors['moisture'] = moisture_adc
        
        print('Alle Sensoren erfolgreich initialisiert!')
        return sensors
        
    except Exception as e:
        print('FEHLER bei Sensor-Initialisierung:', e)
        return None

# =====================================================
# SENSOR FUNKTIONEN
# =====================================================

def validate_sensor_value(value, min_limit, max_limit, sensor_name):
    """
    Validiert Sensorwerte gegen konfigurierte Limits
    Args:
        value: Gemessener Wert
        min_limit: Minimaler erlaubter Wert
        max_limit: Maximaler erlaubter Wert
        sensor_name: Name des Sensors für Debug-Ausgabe
    Returns: True wenn Wert plausibel, False sonst
    """
    if value is None:
        return False
    
    if value < min_limit or value > max_limit:
        if DEBUG_MODE:
            print('WARNUNG: {} Wert außerhalb Limits: {} (erlaubt: {}-{})'.format(
                sensor_name, value, min_limit, max_limit))
        return False
    
    return True

def read_temperature_humidity(sensors):
    """
    Liest Temperatur und Luftfeuchtigkeit vom DHT22 mit Wiederholungsversuchen
    Args:
        sensors: Dictionary mit Sensor-Objekten
    Returns: (temperature, humidity) oder (None, None) bei Fehler
    """
    dht_sensor = sensors.get('dht')
    if not dht_sensor:
        return None, None
    
    for attempt in range(SENSOR_RETRY_COUNT):
        try:
            dht_sensor.measure()
            temperature = dht_sensor.temperature()
            humidity = dht_sensor.humidity()
            
            temp_valid = validate_sensor_value(temperature, TEMP_MIN_LIMIT, TEMP_MAX_LIMIT, "Temperatur")
            humi_valid = validate_sensor_value(humidity, HUMI_MIN_LIMIT, HUMI_MAX_LIMIT, "Luftfeuchtigkeit")
            
            if temp_valid and humi_valid:
                return temperature, humidity
            
        except Exception as e:
            if DEBUG_MODE:
                print('DHT22 Versuch {}/{} fehlgeschlagen: {}'.format(attempt + 1, SENSOR_RETRY_COUNT, e))
            time.sleep(0.5) 
    
    print('FEHLER: DHT22 nach {} Versuchen nicht lesbar'.format(SENSOR_RETRY_COUNT))
    return None, None

def read_distance(sensors):
    """
    Liest Entfernung vom Ultraschallsensor mit Wiederholungsversuchen
    Args:
        sensors: Dictionary mit Sensor-Objekten
    Returns: Entfernung in cm oder None bei Fehler
    """
    ultrasonic_sensor = sensors.get('ultrasonic')
    if not ultrasonic_sensor:
        return None
    
    for attempt in range(SENSOR_RETRY_COUNT):
        try:
            distance = ultrasonic_sensor.distance_cm()
            
            if validate_sensor_value(distance, DIST_MIN_LIMIT, DIST_MAX_LIMIT, "Entfernung"):
                return distance
                
        except Exception as e:
            if DEBUG_MODE:
                print('Ultraschall Versuch {}/{} fehlgeschlagen: {}'.format(attempt + 1, SENSOR_RETRY_COUNT, e))
            time.sleep(0.1)
    
    print('FEHLER: Ultraschallsensor nach {} Versuchen nicht lesbar'.format(SENSOR_RETRY_COUNT))
    return None

def read_soil_moisture(sensors):
    """
    Liest Bodenfeuchtigkeit vom analogen Sensor
    Args:
        sensors: Dictionary mit Sensor-Objekten
    Returns: Roher ADC-Wert (0-4095) oder None bei Fehler
    """
    moisture_sensor = sensors.get('moisture')
    if not moisture_sensor:
        return None
    
    try:
        moisture = moisture_sensor.read()
        
        if DEBUG_MODE:
            if moisture > MOISTURE_DRY_THRESHOLD:
                status = "TROCKEN"
            elif moisture < MOISTURE_WET_THRESHOLD:
                status = "SEHR FEUCHT"
            else:
                status = "FEUCHT"
            #print('Bodenfeuchtigkeit: {} ADC ({})'.format(moisture, status))
        
        return moisture
        
    except Exception as e:
        print('FEHLER beim Lesen des Feuchtigkeitssensors:', e)
        return None

def publish_sensor_data(client, temp, humi, dist, moist):
    """
    Sendet alle Sensordaten via MQTT mit konfigurierbaren Topics
    
    Args:
        client: MQTT Client Objekt
        temp: Temperatur in °C
        humi: Luftfeuchtigkeit in %
        dist: Entfernung in cm
        moist: Bodenfeuchtigkeit (ADC-Wert)
    """
    try:
        temp_msg = b'temp:%.1f' % temp if temp is not None else ERROR_MSG_TEMP
        humi_msg = b'humi:%.1f' % humi if humi is not None else ERROR_MSG_HUMI
        dist_msg = b'distance:%.1f cm' % dist if dist is not None else ERROR_MSG_DIST
        moist_msg = b'moist:%d' % moist if moist is not None else ERROR_MSG_MOIST
        
        print('--- SENSORDATEN ---')
        print('Temperatur:', temp_msg.decode())
        print('Luftfeuchtigkeit:', humi_msg.decode())
        print('Entfernung:', dist_msg.decode())
        print('Bodenfeuchtigkeit:', moist_msg.decode())
        
        if MEMORY_MONITORING:
            print('Freier Speicher:', gc.mem_free(), 'Bytes')
        
        client.publish(TEMP_TOPIC, temp_msg)
        client.publish(HUMI_TOPIC, humi_msg)
        client.publish(DIST_TOPIC, dist_msg)
        client.publish(MOIST_TOPIC, moist_msg)
        
        if DEBUG_MODE:
            print('Daten erfolgreich an MQTT Topics gesendet')
        
    except Exception as e:
        print('FEHLER beim Senden der MQTT-Daten:', e)

# =====================================================
# HAUPTPROGRAMM
# =====================================================

def main():
    """
    Hauptfunktion mit allen konfigurierbaren Parametern aus mysettings.py
    """
    sensors = init_sensors()
    if sensors is None:
        print('KRITISCHER FEHLER: Sensoren konnten nicht initialisiert werden')
        return
    
    # ===== INITIAL-MESSUNG =====
    if DEBUG_MODE:
        print('\n=== ERSTE TESTMESSUNG ===')
        
        try:
            temperature, humidity = read_temperature_humidity(sensors)
            distance = read_distance(sensors)
            moisture = read_soil_moisture(sensors)
            
            print('Test-Messung erfolgreich:')
            print('- Temperatur:', temperature if temperature is not None else 'FEHLER')
            print('- Luftfeuchtigkeit:', humidity if humidity is not None else 'FEHLER')
            print('- Entfernung:', distance if distance is not None else 'FEHLER')
            print('- Bodenfeuchtigkeit:', moisture if moisture is not None else 'FEHLER')
            
        except Exception as e:
            print('FEHLER bei Test-Messung:', e)
    
    # ===== MQTT CLIENT AUS BOOT.PY VERWENDEN =====
    try:
        from boot import client
        print('\n=== HAUPTSCHLEIFE GESTARTET ===')
        print('Messintervall: {} Sekunden'.format(MESSAGE_INTERVAL))
        
    except ImportError:
        print('FEHLER: MQTT Client aus boot.py nicht verfügbar')
        return
    
    # ===== HAUPTSCHLEIFE =====
    last_message_time = 0
    
    while True:
        try:
            client.check_msg()
            
            current_time = time.ticks_ms()
            
            if time.ticks_diff(current_time, last_message_time) >= MESSAGE_INTERVAL * 1000:
                if DEBUG_MODE:
                    print('\n--- NEUE MESSUNG ---')
                
                # Sensoren auslesen
                temperature, humidity = read_temperature_humidity(sensors)
                distance = read_distance(sensors)
                moisture = read_soil_moisture(sensors)
                
                # Daten via MQTT senden
                publish_sensor_data(client, temperature, humidity, distance, moisture)
                
                last_message_time = current_time
                
                if MEMORY_MONITORING:
                    gc.collect()
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print('\n\nProgramm durch Benutzer beendet')
            
            break
            
        except OSError as e:
            print('MQTT Verbindungsfehler:', e)
            try:
                # Versuche Neuverbindung
                from boot import restart_and_reconnect
                restart_and_reconnect()
            except:
                print('Neuverbindung fehlgeschlagen - Programm beendet')
                break
                
        except Exception as e:
            print('UNERWARTETER FEHLER in Hauptschleife:', e)
            if DEBUG_MODE:
                import sys
                sys.print_exception(e)
            
            time.sleep(10)

# =====================================================
# PROGRAMM STARTEN
# =====================================================

if __name__ == "__main__":
    print('\n' + '='*50)
    print('SENSOR SYSTEM HAUPTPROGRAMM GESTARTET')
    print('Konfiguration aus mysettings.py geladen')
    print('='*50)
    
    # Hauptprogramm ausführen
    main()
    
    print('\nSENSOR SYSTEM BEENDET')
else:
    print('main.py als Modul geladen - verwende main() um zu starten')