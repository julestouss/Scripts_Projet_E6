import mysql.connector
from mysql.connector import errorcode
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


try:
    sql_connector = mysql.connector.connect(user='', password='',
                                             host='127.0.0.1', database='ProjetE6_New', port='3306')
    sql_cursor = sql_connector.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

output_file = "/var/lib/mysql-files/tmp_rapports.csv"


def sql_request_outfile():
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Ancien fichier {output_file} supprimé.")

    sql_outfile = f"""
    SELECT id_prise, Donnée
    FROM Prise_Donnée
    INTO OUTFILE '{output_file}'
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n';
    """

    try:
        sql_cursor.execute(sql_outfile)
        print(f"Les données ont étées exportées vers {output_file}")
    except mysql.connector.Error as err:
        print(err)


def sql_request_getusr(prise_id):
    sql_select = "SELECT UPN_utilisateur FROM Utilisateur_PC_Prise WHERE id_prise = %s;"

    try:
        # Exécution de la requête en utilisant un paramètre
        sql_cursor.execute(sql_select, (prise_id,))  # Mise de prise_id dans un tuple
        result = sql_cursor.fetchone()  # Récupère le premier et unique résultat
        if result:
            return result[0]
        else:
            return None
    except mysql.connector.Error as err:
        print(err)
        return None


def sql_request_truncate():
    sql_trunc = "TRUNCATE TABLE Prise_Donnée"
    try:
        sql_cursor.execute(sql_trunc)
        sql_connector.commit()
    except mysql.connector.Error as err:
        print(err)


def calc_conso(donnees):
    return sum(donnee * 230 for donnee in donnees) / (21.4 * 25200)  # Calculer la consommation en watt moyen par jour


def send_mail(moyenne, id_prise):
    # Récupérer l'utilisateur lié à la prise (doit être une adresse email valide)
    destinataire = sql_request_getusr(id_prise)
    if not destinataire:
        print(f"Impossible de trouver l'utilisateur pour la prise {id_prise}. Email non envoyé.")
        return

    # Configuration SMTP pour Office 365
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = ""
    sender_password = ""  # Attention : Pense à utiliser un mot de passe d’application si nécessaire

    # Création du message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = destinataire
    msg["Subject"] = f"Consommation de votre prise {id_prise}"

    # Corps du mail
    body = f"""
    Bonjour,

    Voici votre rapport de consommation électrique :

    📌 Prise ID : {id_prise}
    ⚡ Consommation moyenne : {moyenne:.2f} W/jour

    Pensez à optimiser votre consommation d’énergie !

    Cordialement,
    Votre service de gestion d'énergie
    """
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connexion au serveur et envoi du mail
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Sécurise la connexion
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinataire, msg.as_string())
        server.quit()
        print(f"Email envoyé à {destinataire} pour la prise {id_prise}.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")


def using_csv():
    # Ouvrir le fichier CSV en mode lecture
    with open(output_file, mode='r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile, fieldnames=["id_prise", "Donnée"])  # Lire les lignes sous forme de dictionnaire

        data_donnees = {}  # Dictionnaire pour stocker les données par prise

        # Organiser les données par id_prise
        for ligne in csv_reader:
            id_prise = ligne['id_prise']
            donnee = int(ligne['Donnée'])  # Convertir la donnée en entier

            if id_prise not in data_donnees:
                data_donnees[id_prise] = []  # Créer une liste si elle n'existe pas
            data_donnees[id_prise].append(donnee)  # Ajouter la donnée à la liste

    # Calculer la consommation et envoyer l'email
    for id_prise, donnees in data_donnees.items():
        moyenne = calc_conso(donnees)  # Calcul de la consommation
        send_mail(moyenne, id_prise)  # Envoi de l'email

# Exécution des fonctions
sql_request_outfile()  # Génère le CSV
using_csv()  # Lit le CSV, calcule la conso et envoie les mails
sql_request_truncate()  # Efface les données de la table après traitement
