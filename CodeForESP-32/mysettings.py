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
MOISTURE_SENSOR_PIN = 34  

# BMP280 Pins (nicht verwendet, war aber bereits im Code)
BMP280_SCL_PIN = 22  
BMP280_SDA_PIN = 21  

# === AKTOREN ===

# Lüfter Steuerung
LUEFTER_RELAIS_PIN = 23    
LUEFTER_PWM_PIN = 32       
LUEFTER_PWM_FREQ = 50      
LUEFTER_PWM_DUTY_ON = 70   
LUEFTER_PWM_DUTY_OFF = 18  

# Pumpen Steuerung
PUMPE_RELAIS_PIN = 19  

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
MQTT_PORT = 1883           
MQTT_QOS_LEVEL = 1        
MQTT_RETAIN_MESSAGES = True

# =====================================================
# MQTT TOPICS FÜR SENSORDATEN
# =====================================================

TEMP_TOPIC = b'DLN/test/temp'        # Temperatur vom DHT22
HUMI_TOPIC = b'DLN/test/humi'        # Luftfeuchtigkeit vom DHT22  
DIST_TOPIC = b'DLN/test/dist'        # Entfernung vom Ultraschallsensor
MOIST_TOPIC = b'DLN/test/moist'      # Bodenfeuchtigkeit vom analogen Sensor

# =====================================================
# MQTT TOPICS FÜR AKTOREN 
# =====================================================

LUEFTER_TOPIC = b'DLN/test/luefter'  # Lüfter-Steuerung
PUMPE_TOPIC = b'DLN/test/pumpe'      # Pumpen-Steuerung 

# =====================================================
# MQTT SYSTEM TOPICS
# =====================================================

# Topic für allgemeine Benachrichtigungen an das Gerät
NOTIFICATION_TOPIC = b'DLN/test/notification'

# Last Will Topic - wird automatisch gesendet wenn Verbindung verloren geht
STATUS_TOPIC = b'DLN/test/status'



DEBUG_MODE = True

MEMORY_MONITORING = True

AUTO_RESTART_ON_ERROR = False

MSG_DEVICE_ONLINE = " ist online"
MSG_DEVICE_OFFLINE = " ist offline"

CMD_ON = b'on'
CMD_OFF = b'off'
CMD_RECEIVED = b'received'

ERROR_MSG_TEMP = b'temp:ERROR'
ERROR_MSG_HUMI = b'humi:ERROR'  
ERROR_MSG_DIST = b'distance:ERROR'
ERROR_MSG_MOIST = b'moist:ERROR'

# =====================================================
# LIMITS
# =====================================================

TEMP_MIN_LIMIT = -40   
TEMP_MAX_LIMIT = 80     
HUMI_MIN_LIMIT = 0     
HUMI_MAX_LIMIT = 100   
DIST_MIN_LIMIT = 2      
DIST_MAX_LIMIT = 400  

SENSOR_RETRY_COUNT = 3