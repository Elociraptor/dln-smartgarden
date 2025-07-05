# =====================================================
# ZENTRALE KONFIGURATIONSDATEI FÜR SENSOR SYSTEM
# =====================================================

# =====================================================
# HARDWARE PIN KONFIGURATION
# =====================================================
from machine import ADC, Pin

# === SENSOREN ===
# DHT22 Temperatursensor Pin

DHT22PIN = 21

# HC-SR04 Ultraschallsensor Pins
ULTRASONIC_TRIGGER_PIN = 26
ULTRASONIC_ECHO_PIN = 14
ULTRASONIC_TIMEOUT_US = 10000  # Timeout in Mikrosekunden

# Bodenfeuchtigkeitssensor (analoger Sensor)
MOISTURE_SENSOR_PIN = 34  # ADC Pin

# BMP280 Drucksensor I2C Pins (nicht verwendet, war aber bereits im Code)
BMP280_SCL_PIN = 22  # Serial Clock Line
BMP280_SDA_PIN = 21  # Serial Data Line

# === AKTOREN ===
# Lüfter Steuerung
LUEFTER_RELAIS_PIN = 23    # Digital Pin für Relais
LUEFTER_PWM_PIN = 32       # PWM Pin für Drehzahlsteuerung
LUEFTER_PWM_FREQ = 50      # PWM Frequenz in Hz
LUEFTER_PWM_DUTY_ON = 70   # PWM Duty Cycle wenn AN (0-100%)
LUEFTER_PWM_DUTY_OFF = 18  # PWM Duty Cycle wenn AUS

# Pumpen Steuerung
PUMPE_RELAIS_PIN = 19     # Digital Pin für Pumpen-Relais

# =====================================================
# ADC (ANALOG-DIGITAL-CONVERTER) EINSTELLUNGEN
# =====================================================

# ADC Konfiguration für Feuchtigkeitssensor
ADC_WIDTH = ADC.WIDTH_12BIT    # 12-bit Auflösung (0-4095)
ADC_ATTENUATION = ADC.ATTN_11DB # Messbereich bis ~3.3V

# Bodenfeuchtigkeits-Schwellwerte für Interpretation
MOISTURE_DRY_THRESHOLD = 2000     # Werte über diesem Wert = trocken
MOISTURE_WET_THRESHOLD = 1500     # Werte unter diesem Wert = sehr feucht

# =====================================================
# TIMING UND INTERVALLE
# =====================================================

# Messintervall zwischen Sensormessungen (in Sekunden)
MESSAGE_INTERVAL = 10

# WLAN Verbindungs-Timeout (in Sekunden)
WLAN_TIMEOUT = 20

# MQTT Keep-Alive Intervall (in Sekunden)
MQTT_KEEPALIVE = 30

# Neuverbindungs-Wartezeit bei Fehlern (in Sekunden)
RECONNECT_DELAY = 30

# =====================================================
# MQTT BROKER KONFIGURATION
# =====================================================

# MQTT Broker Server Adresse
# Kann IP-Adresse oder Domain-Name sein
MQTT_SERVER = 'broker.f4.htw-berlin.de'

# MQTT Verbindungsparameter
MQTT_PORT = 1883           # Standard MQTT Port
MQTT_QOS_LEVEL = 1         # Quality of Service Level (0, 1, oder 2)
MQTT_RETAIN_MESSAGES = True # Nachrichten auf Broker speichern

# =====================================================
# MQTT TOPICS FÜR SENSORDATEN (PUBLISH)
# =====================================================
# Diese Topics werden zum Senden von Sensordaten verwendet

TEMP_TOPIC = b'DLN/test/temp'        # Temperatur vom DHT22
HUMI_TOPIC = b'DLN/test/humi'        # Luftfeuchtigkeit vom DHT22  
DIST_TOPIC = b'DLN/test/dist'        # Entfernung vom Ultraschallsensor
MOIST_TOPIC = b'DLN/test/moist'      # Bodenfeuchtigkeit vom analogen Sensor

# =====================================================
# MQTT TOPICS FÜR AKTOREN (SUBSCRIBE)
# =====================================================
# Diese Topics werden zum Empfangen von Steuerbefehlen verwendet

LUEFTER_TOPIC = b'DLN/test/luefter'  # Lüfter-Steuerung (on/off)
PUMPE_TOPIC = b'DLN/test/pumpe'      # Pumpen-Steuerung (on/off)

# =====================================================
# MQTT SYSTEM TOPICS
# =====================================================

# Topic für allgemeine Benachrichtigungen an das Gerät
NOTIFICATION_TOPIC = b'DLN/test/notification'

# Last Will Topic - wird automatisch gesendet wenn Verbindung verloren geht
STATUS_TOPIC = b'DLN/test/status'

# =====================================================
# SYSTEM EINSTELLUNGEN
# =====================================================

# Debug-Modus aktivieren (mehr Ausgaben)
DEBUG_MODE = True

# Speicher-Monitoring aktivieren
MEMORY_MONITORING = True

# Automatischer Neustart bei kritischen Fehlern
AUTO_RESTART_ON_ERROR = False

# =====================================================
# NACHRICHTEN TEMPLATES
# =====================================================

# Status-Nachrichten für MQTT
MSG_DEVICE_ONLINE = " ist online"
MSG_DEVICE_OFFLINE = " ist offline"

# Aktor-Befehle (was das System erwartet)
CMD_ON = b'on'
CMD_OFF = b'off'
CMD_RECEIVED = b'received'

# Fehler-Nachrichten in Sensordaten
ERROR_MSG_TEMP = b'temp:ERROR'
ERROR_MSG_HUMI = b'humi:ERROR'  
ERROR_MSG_DIST = b'distance:ERROR'
ERROR_MSG_MOIST = b'moist:ERROR'

# =====================================================
# KALIBRIERUNG UND LIMITS
# =====================================================

# Sensor-Limits für Plausibilitätsprüfung
TEMP_MIN_LIMIT = -40    # Minimale erlaubte Temperatur (°C)
TEMP_MAX_LIMIT = 80     # Maximale erlaubte Temperatur (°C)
HUMI_MIN_LIMIT = 0      # Minimale erlaubte Luftfeuchtigkeit (%)
HUMI_MAX_LIMIT = 100    # Maximale erlaubte Luftfeuchtigkeit (%)
DIST_MIN_LIMIT = 2      # Minimale messbare Entfernung (cm)
DIST_MAX_LIMIT = 400    # Maximale messbare Entfernung (cm)

# Anzahl der Wiederholungsversuche bei Sensor-Fehlern
SENSOR_RETRY_COUNT = 3

# =====================================================
# BACKWARDS COMPATIBILITY
# =====================================================
# Alte Variablennamen für Kompatibilität mit bestehendem Code
# DEPRECATED - wird in zukünftigen Versionen entfernt

message_interval = MESSAGE_INTERVAL
mqtt_server = MQTT_SERVER
temp_topic = TEMP_TOPIC
humi_topic = HUMI_TOPIC
dist_topic = DIST_TOPIC
moist_topic = MOIST_TOPIC
luefter_topic = LUEFTER_TOPIC
pumpe_topic = PUMPE_TOPIC
topic_sub = NOTIFICATION_TOPIC
last_will_topic = STATUS_TOPIC