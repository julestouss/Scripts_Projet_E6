import mysql.connector
from mysql.connector import errorcode
import paho.mqtt.client as mqtt
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

# connection à la base de données
try:
    sql_connector = mysql.connector.connect(user = '', password = '',
                                    host='', database='ProjetE6_New', port='')
    sql_cursor = sql_connector.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

# connection au brocker

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="python-1", transport='tcp', protocol=mqtt.MQTTv5)
client.tls_set(ca_certs="ca.crt", certfile="python.crt", keyfile="python_no_passphrase.key")
client.tls_insecure_set(True)
# Callback lors de la connexion
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connecté avec le code {reason_code}")
    client.subscribe("conso/#")



# Callback lors de la réception d'un message
def on_message(client, userdata, message):
        id_prise = message.topic.replace("conso/", "", 1)
        donnee = message.payload.decode()

        sql_insert = "INSERT INTO Prise_Donnée (id_prise, Donnée) VALUES(%s, %s);"
        sql_val = (id_prise, donnee)
        print(f"Message reçu sur `{id_prise}` : {donnee} ")
        sql_cursor.execute(sql_insert, sql_val)
        sql_connector.commit()

# Enregistrement des callbacks
client.on_connect = on_connect
client.on_message = on_message


brocker_addr = ''
pPort = 

# définie les propriétés de connexion MQTTv5
pProperties=Properties(PacketTypes.CONNECT)
# Garde la session active pendant 30 minutes après la déconnexion
pProperties.SessionExpiryInterval=30*60 # in seconds
client.connect(brocker_addr,
               port=pPort,
               clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
               properties=pProperties,
               keepalive=60);

# commencer une boucle infinie ou l'on publie les données qui arrive sur le broker dans la base de données tant que le programme tourne
try:
    print("Démarrage du client MQTT et du connecteur MySQL... (Appuyez sur Ctrl+C pour arrêter)")
    client.loop_forever()
except KeyboardInterrupt:
    print("\nInterruption détectée. Arrêt du client MQTT et du connecteur MySQL...")
    client.disconnect()
    sql_connector.close()