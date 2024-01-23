import mysql.connector

# Connessione al Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ingSw"
)
cursor = db.cursor()

# METODI PER L'AUTENTICAZIONE

def isMatricola(matricola):
    sql = "SELECT * FROM studenti WHERE matricola = %s;"
    cursor.execute(sql, (matricola,))
    result = cursor.fetchone()
    return result[0] if result else None

def getPassword(matricola):
    sql = "SELECT * FROM studenti WHERE matricola = %s;"
    cursor.execute(sql, (matricola,))
    result = cursor.fetchone()
    return result[1] if result else None

# METODI PER LA RELAZIONE CORSI

def getCorsi():
    sql = "SELECT * FROM corsi;"
    cursor.execute(sql)
    return cursor.fetchall()

def getCorso(id):
    sql = "SELECT descrizione FROM corsi WHERE id = %s;"
    cursor.execute(sql, (id,))
    return cursor.fetchone()[0]

def getPostiCorso(corso_id):
    sql = "SELECT posti_disponibili FROM corsi WHERE id = %s;"
    cursor.execute(sql, (corso_id,))
    return cursor.fetchone()[0]

def eliminaPostoCorso(corso_id):
    sql = "UPDATE corsi SET posti_disponibili = posti_disponibili - 1 WHERE id = %s;"
    cursor.execute(sql, (corso_id,))
    db.commit()

def aggiungiPostoCorso(corso_id):
    sql = "UPDATE corsi SET posti_disponibili = posti_disponibili + 1 WHERE id = %s;"
    cursor.execute(sql, (corso_id,))
    db.commit()

def prenotazioneGiaEffettuata(matricola, corso_id):
    res = getPrenotazioni(matricola)
    for riga in res:
        if int(riga[2]) == int(corso_id):
            return True

# METODI PER LA RELAZIONE PRENOTAZIONI

def prenotaPostoCorso(matricola, corso_id):
    sql = "SELECT data_ora FROM corsi WHERE id = %s"
    cursor.execute(sql, (corso_id,))
    data_ora = cursor.fetchone()[0]

    sql1 = "INSERT INTO prenotazioni (matricola, id_corso, data_ora) VALUES (%s, %s, %s);"
    cursor.execute(sql1, (matricola, corso_id, data_ora))
    db.commit()

def getPrenotazioni(matricola):
    sql = "SELECT * FROM prenotazioni WHERE matricola = %s;"
    cursor.execute(sql, (matricola,))
    return cursor.fetchall()

def deletePrenotazione(id):
    sql = "DELETE FROM prenotazioni WHERE id = %s;"
    cursor.execute(sql, (id,))
    db.commit()

def fixPostiCorsoFromDeletePrenotazione(id):
    sql = "SELECT id_corso FROM prenotazioni WHERE id = %s;"
    cursor.execute(sql, (id,))
    corso_id = cursor.fetchone()[0]
    aggiungiPostoCorso(corso_id)

def getCorsoFromPrenotazione(id):
    sql = "SELECT id_corso FROM prenotazioni WHERE id = %s;"
    cursor.execute(sql, (id,))
    corso_id = cursor.fetchone()[0]
    return getCorso(corso_id)