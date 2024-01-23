import bcrypt

#Funzione per hashare la password
def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password


#La password è quella inserita dall'utente, l'hashed password è quella presa dal db.
def verify_password(password, hashed_password):
     # Assicurati che entrambi, password e hashed_password, siano in formato bytes
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    # Verifica la password
    return bcrypt.checkpw(password, hashed_password)

