# =====================================================
# BOOT.PY - SYSTEM INITIALISIERUNG
# =====================================================
# Diese Datei wird beim Start des ESP32/ESP8266 automatisch ausgeführt
# Alle konfigurierbaren Parameter sind jetzt in mysettings.py!
# =====================================================

# =====================================================
# IMPORT SECTION
# =====================================================

# System und Hardware Imports
import time
import machine
import micropython
import network
import esp
import gc
import ubinascii

# Hardware Control Imports
from machine import Pin, PWM

# MQTT Client Import
from umqttsimple import MQTTClient

# Zentrale Konfiguration importieren
from mysettings import (
    # MQTT Konfiguration
    MQTT_SERVER,
    MQTT_KEEPALIVE,
    MQTT_QOS_LEVEL,
    MQTT_RETAIN_MESSAGES,
    
    # Topics
    NOTIFICATION_TOPIC,
    STATUS_TOPIC,
    LUEFTER_TOPIC,
    PUMPE_TOPIC,
    
    # Hardware Pins
    LUEFTER_RELAIS_PIN,
    LUEFTER_PWM_PIN,
    LUEFTER_PWM_FREQ,
    LUEFTER_PWM_DUTY_ON,
    LUEFTER_PWM_DUTY_OFF,
    PUMPE_RELAIS_PIN,
    
    # System Einstellungen
    WLAN_TIMEOUT,
    RECONNECT_DELAY,
    DEBUG_MODE,
    AUTO_RESTART_ON_ERROR,
    
    # Nachrichten
    MSG_DEVICE_ONLINE,
    MSG_DEVICE_OFFLINE,
    CMD_ON,
    CMD_OFF,
    CMD_RECEIVED
)

# WLAN Credentials
from mysecrets import my_SSID as ssid, my_PW as password

# =====================================================
# SYSTEM INITIALISIERUNG
# =====================================================

esp.osdebug(None)

gc.collect()
print('=== SYSTEM START ===')
if DEBUG_MODE:
    print('Debug-Modus: AKTIVIERT')
    print('Freier Speicher:', gc.mem_free(), 'Bytes')

# =====================================================
# MQTT CLIENT SETUP
# =====================================================

myclient_id = ubinascii.hexlify(machine.unique_id())
if DEBUG_MODE:
    print('MQTT Client ID:', myclient_id)

last_message = 0

# =====================================================
# WLAN VERBINDUNGS-FUNKTIONEN
# =====================================================

def do_connect():
    """
    Stellt WLAN-Verbindung her
    Returns: WLAN-Objekt bei erfolgreicher Verbindung, None bei Fehler
    """
    if DEBUG_MODE:
        print('\n=== WLAN VERBINDUNG ===')
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Verbinde mit Netzwerk:', ssid)
        wlan.connect(ssid, password)
        
        timeout = 0
        while not wlan.isconnected() and timeout < WLAN_TIMEOUT:
            if DEBUG_MODE:
                print('.', end='')
            time.sleep(1)
            timeout += 1
        
        if not wlan.isconnected():
            print('\nFEHLER: WLAN Verbindung nach {}s fehlgeschlagen!'.format(WLAN_TIMEOUT))
            return None
    
    print('\nWLAN erfolgreich verbunden!')
    if DEBUG_MODE:
        print('Netzwerk Konfiguration:', wlan.ifconfig())
    return wlan

# =====================================================
# HARDWARE CONTROL FUNKTIONEN
# =====================================================

def init_hardware():
    """
    Initialisiert alle Hardware-Pins für Aktoren
    Returns: Dictionary mit Hardware-Objekten
    """
    if DEBUG_MODE:
        print('\n=== HARDWARE INITIALISIERUNG ===')
    
    hardware = {
        'luefter_relais': Pin(LUEFTER_RELAIS_PIN, Pin.OUT),
        'pumpe_relais': Pin(PUMPE_RELAIS_PIN, Pin.OUT),
        'luefter_pwm': PWM(Pin(LUEFTER_PWM_PIN), freq=LUEFTER_PWM_FREQ)
    }
    
    # Aktoren initial ausschalten
    hardware['luefter_relais'].off()
    hardware['pumpe_relais'].off()
    hardware['luefter_pwm'].duty(LUEFTER_PWM_DUTY_OFF)
    
    if DEBUG_MODE:
        print('Hardware initialisiert:')
        print('- Lüfter Relais Pin:', LUEFTER_RELAIS_PIN)
        print('- Lüfter PWM Pin:', LUEFTER_PWM_PIN)
        print('- Pumpe Relais Pin:', PUMPE_RELAIS_PIN)
    
    return hardware

def control_luefter(command, hardware):
    """
    Steuert den Lüfter basierend auf Befehl
    Args:
        command: CMD_ON oder CMD_OFF
        hardware: Hardware Dictionary
    """
    luefter_relais = hardware['luefter_relais']
    luefter_pwm = hardware['luefter_pwm']
    
    if command == CMD_ON:
        print('>>> LÜFTER EINSCHALTEN')
        luefter_relais.on()
        luefter_pwm.duty(LUEFTER_PWM_DUTY_ON)
        
    elif command == CMD_OFF:
        print('>>> LÜFTER AUSSCHALTEN')
        luefter_pwm.duty(LUEFTER_PWM_DUTY_OFF)
        luefter_relais.off()
        
    else:
        print('Unbekannter Lüfter-Befehl:', command)

def control_pumpe(command, hardware):
    """
    Steuert die Pumpe basierend auf Befehl
    Args:
        command: CMD_ON oder CMD_OFF
        hardware: Hardware Dictionary
    """
    pumpe_relais = hardware['pumpe_relais']
    
    if command == CMD_ON:
        print('>>> PUMPE EINSCHALTEN')
        pumpe_relais.on()
        
    elif command == CMD_OFF:
        print('>>> PUMPE AUSSCHALTEN')
        pumpe_relais.off()
        
    else:
        print('Unbekannter Pumpen-Befehl:', command)

# =====================================================
# MQTT CALLBACK FUNKTIONEN
# =====================================================

hardware_devices = None

def sub_cb(topic, msg):
    """
    Callback-Funktion für eingehende MQTT-Nachrichten
    
    Args:
        topic: MQTT Topic der Nachricht
        msg: Nachrichteninhalt
    """
    global hardware_devices
    
    if DEBUG_MODE:
        print('MQTT Nachricht empfangen:', topic, msg)
    
    # ===== ALLGEMEINE BENACHRICHTIGUNGEN =====
    if topic == NOTIFICATION_TOPIC and msg == CMD_RECEIVED:
        print('Bestätigung: ESP hat Nachricht empfangen')
    
    # ===== PUMPEN-STEUERUNG =====
    elif topic == PUMPE_TOPIC:
        control_pumpe(msg, hardware_devices)
    
    # ===== LÜFTER-STEUERUNG =====
    elif topic == LUEFTER_TOPIC:
        control_luefter(msg, hardware_devices)
    
    else:
        if DEBUG_MODE:
            print('Unbekanntes Topic:', topic)

# =====================================================
# MQTT VERBINDUNGS-FUNKTIONEN
# =====================================================

def connect_and_subscribe():
    """
    Verbindet mit MQTT-Broker und abonniert Topics
    Returns: MQTT Client Objekt
    """
    if DEBUG_MODE:
        print('\n=== MQTT VERBINDUNG ===')
    
    try:
        client = MQTTClient(
            client_id=myclient_id,
            server=MQTT_SERVER,
            keepalive=MQTT_KEEPALIVE
        )
        
        client.set_last_will(
            STATUS_TOPIC,
            str(myclient_id) + MSG_DEVICE_OFFLINE,
            retain=MQTT_RETAIN_MESSAGES,
            qos=MQTT_QOS_LEVEL
        )
        
        client.set_callback(sub_cb)
        
        client.connect()
        print('Mit MQTT Broker verbunden:', MQTT_SERVER)
        
        # Topics abonnieren
        topics_to_subscribe = [NOTIFICATION_TOPIC, PUMPE_TOPIC, LUEFTER_TOPIC]
        for topic in topics_to_subscribe:
            client.subscribe(topic)
            if DEBUG_MODE:
                print('Topic abonniert:', topic)
        
        client.publish(
            STATUS_TOPIC,
            str(myclient_id) + MSG_DEVICE_ONLINE,
            retain=MQTT_RETAIN_MESSAGES,
            qos=MQTT_QOS_LEVEL
        )
        
        print('MQTT Setup erfolgreich abgeschlossen')
        if DEBUG_MODE:
            print('Client-ID:', myclient_id)
        return client
        
    except Exception as e:
        print('FEHLER bei MQTT Verbindung:', e)
        raise

def restart_and_reconnect():
    """
    Behandelt Verbindungsabbrüche mit konfigurierbarer Wartezeit
    """
    print('FEHLER: MQTT Verbindung verloren. Neuverbindung in {}s...'.format(RECONNECT_DELAY))
    time.sleep(RECONNECT_DELAY)
    
    if AUTO_RESTART_ON_ERROR:
        print('Automatischer Neustart aktiviert...')
        machine.reset()

# =====================================================
# HAUPTPROGRAMM - SYSTEM START
# =====================================================

print('\n=== INITIALISIERUNG STARTEN ===')

hardware_devices = init_hardware()

# WLAN-Verbindung herstellen
wlan = do_connect()
if wlan is None:
    print('KRITISCHER FEHLER: Keine WLAN-Verbindung möglich')
    if AUTO_RESTART_ON_ERROR:
        machine.reset()

# MQTT-Verbindung herstellen
try:
    client = connect_and_subscribe()
    print('\n=== SYSTEM BEREIT ===')
    if DEBUG_MODE:
        print('Freier Speicher:', gc.mem_free(), 'Bytes')
        print('Konfiguration geladen aus mysettings.py')
    
except OSError as e:
    print('KRITISCHER FEHLER bei MQTT Setup:', e)
    restart_and_reconnect()