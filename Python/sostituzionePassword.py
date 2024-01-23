#QUESTO SCRIPT HA IL SOLO SCOPO DI HASHARE TUTTE LE PASSWORD PRESENTI NEL DB. VA LANCIATO UNA SOLA VOLTA

import mysql.connector
import bcrypt

# Connessione al Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ingSw"
)
cursor = db.cursor()

# Funzione per hashare la password
def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password

# Estrai tutte le password
def estrai_password():
    sql = "SELECT matricola, password FROM studenti;"
    cursor.execute(sql)
    return cursor.fetchall()

# Aggiorna le password nel database
def aggiorna_password(matricola, hashed_password):
    sql = "UPDATE studenti SET password = %s WHERE matricola = %s;"
    cursor.execute(sql, (hashed_password, matricola))
    db.commit()

# Script per hashare e aggiornare le password
def hash_e_aggiorna_password():
    studenti = estrai_password()
    for matricola, password in studenti:
        hashed_password = hash_password(password)
        aggiorna_password(matricola, hashed_password)

# Esegui lo script
hash_e_aggiorna_password()

# Chiudi la connessione
db.close()
