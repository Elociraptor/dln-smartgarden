# Smart Garden System
## Kurzbeschreibung

Dieses Projekt realisiert ein automatisiertes Smart-Garden-System, das Umweltparameter in einem Gewächshaus überwacht und regelt. Es nutzt einen ESP32 für Sensoren/Aktoren, einen Raspberry Pi mit Node-RED für die Logik und MQTT für die Echtzeitkommunikation.

## Einrichtung
### Node-RED auf dem Raspberry-PI starten

Per SSH mit dem Raspberry-PI verbinden und Node-RED starten. 

(Die Zahl nach 10.10.4. ändert sich je nach verwedetem Raspberry-PI, es ist immer 150 + die Boxnummer)

```bash
 ssh pi@10.10.4.156
```

Das Passwort ist: 1Himbeere

```bash
 node-red start
```

Danach http://10.10.4.156:1880/ (ebenfalls mit angepasster Nummer) aufrufen und Node-RED flow von [hier](https://github.com/Elociraptor/dln-smartgarden/tree/main/NodeRed-flow) laden.

### ESP-32 Einrichten

[Thonny IDE](https://thonny.org/) installieren/öffnen. 

ESP-32 mit dem Kabel an den PC verbinden.

Micropython Code von [hier](https://github.com/Elociraptor/dln-smartgarden/tree/main/CodeForESP-32) laden, und auf den ESP überspielen.

Prüfen ob gesamte Verkableung richtig ist. (Pins sind in der mySettings.py aufgelistet)

Programm staten

### Dashboard aufrufen

http://10.10.4.156:1880/ui aufrufen (ebenfalls mit angepasster Nummer).


### Kontrolle

Zur Kontrolle kann ebenfalls die MQTT Topic auf dem PC abboniert werden. 

Dafür ist [Mosquitto](https://mosquitto.org/) erforderlich.

```bash
 mosquitto_sub -h broker.f4.htw-berlin.de -t "DLN/test/#" -v
```