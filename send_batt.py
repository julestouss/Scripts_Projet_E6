import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes
import psutil
import socket
import time

def get_batt():
    battery = psutil.sensors_battery()
    return round(battery.percent)

# Fonction qui publie le niveau de batterie toutes les secondes
def publish_battery():
    hostename = socket.gethostname()
    # Paramètres du broker MQTT
    broker_addr = "192.168.27.102"  
    pPort = 8883
    topic = f"batterie/{hostename}"
    
    # Créer un client MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="python-pc", transport='tcp', protocol=mqtt.MQTTv5)
    client.tls_set(ca_certs="certs/ca.crt", certfile="certs/client.crt", keyfile="certs/client_no_passphrase.key")
    client.tls_insecure_set(True)

    # Fonction de callback lors de la connexion
    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"Connected to {broker_addr} with result code {rc}")
        
    # Fonction de callback lors de la publication
    def on_publish(client, userdata, mid, reason_code=None, properties=None):
        print(f"Message {mid} publié sur {topic}")
    
    # Ajouter les callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish

    pProperties=Properties(PacketTypes.CONNECT)
    pProperties.SessionExpiryInterval=30*60
    # Se connecter au broker
    client.connect(broker_addr,
               port=pPort,
               clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
               properties=pProperties,
               keepalive=60);
    try:
        # Boucle de publication toutes les secondes
        while True:
            # Récupérer le pourcentage de batterie
            battery_level = get_batt()
            
            # Publier sur le topic
            payload = f"Batterie: {battery_level}%"
            client.publish(topic, payload)

            # Attendre 1 seconde avant de republier
            time.sleep(1)

        # Boucle pour maintenir la connexion
        
        client.loop_forever()
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()

# Appeler la fonction de publication
publish_battery()

