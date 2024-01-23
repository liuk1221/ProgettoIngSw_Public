#Imports
import telebot
import db #Importo il mio file db
from telebot import types 
import hash
import json

#IMPORT API KEY
with open('config.json') as f:
    config = json.load(f)

#Collegamento con il bot
API_TOKEN = config["api_token"]
bot = telebot.TeleBot(API_TOKEN, parse_mode=None) 

#Dict per tracciare la conversazione e i dati ottenuti.Dict per gli stati utente.
user_data={}
user_state={}

#Stati Utente
class States:
    S_START = "start"  #Stato iniziale
    S_ENTER_MATRICOLA = "enter_matricola"  #Aspettando la matricola
    S_ENTER_PASSWORD = "enter_password"  #Aspettando la password
    S_AUTHENTICATED = "authenticated"  #Autenticazione completata

#PrimoMessaggio
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == States.S_START or message.text in ["/start", "/help"])
def start(message):
    chat_id = message.chat.id
    #Svuota UserData in caso di uscita
    user_data[chat_id]={}
    bot.reply_to(message, "Autenticazione necessaria. Inserire la propria matricola:")
    #Porta lo UserState a InserimentoMatricola
    user_state[chat_id] = States.S_ENTER_MATRICOLA

#------------------- AUTENTICAZIONE ----------------------
#Inserimento, verifica della matricola e inserimento, verifica della password.
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == States.S_ENTER_MATRICOLA)
def verificaMatricola(message):
    chat_id = message.chat.id
    if message.text.isdigit() and len(message.text) == 6:
        #Il messaggio è composto da 6 cifre numeriche, salviamolo in variabile
        matricola = int(message.text)
        user_data[message.chat.id] = {"matricola": matricola}  #Salva la matricola nell'user_data. Utilizzo chat_id in modo che sia tutto univoco verso quella sessione.
        bot.send_message(chat_id, "Il numero inserito è valido. Ricerca di "+str(matricola))

        #Chiamata al metodo del DB e verifica della matricola inserita
        if db.isMatricola(matricola) != None:
            bot.reply_to(message, "La matricola è stata trovata. Inserire la password:")
            #Passiamo all'inserimento e alla verifica della password
            user_state[chat_id] = States.S_ENTER_PASSWORD
        else:
            bot.reply_to(message, "La matricola non è stata trovata. Riprovare:")
    else:
        #Il messaggio non è composto da 6 cifre numeriche
        bot.send_message(chat_id, "Non è stata inserita una matricola. Inserisci esattamente 6 cifre numeriche valide.")
        user_state[chat_id] = States.S_ENTER_MATRICOLA #Superfluo ma per maggiore chiarezza

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == States.S_ENTER_PASSWORD)
def verificaPassword(message):
    chat_id = message.chat.id
    if chat_id in user_data and "matricola" in user_data[chat_id]:
        matricola = user_data[chat_id]["matricola"]
        password = db.getPassword(matricola) #Password presa dall'utente.
        password_inserita = message.text #Password inserita in chat.
        bot.delete_message(chat_id, message.message_id)
        if hash.verify_password(password_inserita, password):
            bot.send_message(chat_id, "La password inserita è corretta. Autenticazione avvenuta con successo di "+str(user_data[chat_id]["matricola"])+".")
            user_state[chat_id] = States.S_AUTHENTICATED
            #Vado direttamente al menu'
            mostraMenu(message)
        else:
            bot.send_message(chat_id, "La password inserita non è corretta. Riprovare:")
            # Ritorno all'inizio del metodo verifica password
            user_state[chat_id] = States.S_ENTER_PASSWORD #Superfluo ma per maggiore chiarezza
    else:
        bot.reply_to(message, "Errore: matricola non trovata nella sessione corrente.")
#-------------------------------------------------------
#Menu' di scelta
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == States.S_AUTHENTICATED)
def mostraMenu(message):
    chat_id = message.chat.id 
    
    #Creo il markup inline
    markup = types.InlineKeyboardMarkup()

    #Creo i bottoni
    btn1 = types.InlineKeyboardButton("Visualizza corsi", callback_data='op1')
    btn2 = types.InlineKeyboardButton("Visualizza prenotazioni", callback_data='op2')
    btn3 = types.InlineKeyboardButton("Esci", callback_data='op3')

    #Aggiungo i bottoni al markup
    markup.add(btn1,btn2,btn3)

    bot.send_message(chat_id, "Scegli un opzione dal menu:", reply_markup=markup)

#Handler menu
@bot.callback_query_handler(func=lambda call: call.data in ['op1', 'op2', 'op3'])
def chiamatBottoni(c):
    chat_id = c.message.chat.id
    # Controlla se l'utente è ancora in uno stato che gli permette di usare il menu
    if user_state.get(chat_id) != States.S_AUTHENTICATED:
        bot.send_message(chat_id, "Sessione terminata o non valida.")
        return

    chat_id = c.message.chat.id
    if c.data == "op1":
        #Chiamata alla funzione per stampare tutti i corsi disponibili
        mostraCorsi(c.message)

    elif c.data == "op2":
        #Chiamata alla funzione per stampare tutte le prenotazioni effettuate
        mostraPrenotazioni(c.message)
    elif c.data == "op3":
        bot.send_message(c.message.chat.id, "Arrivederci!")
        user_state[chat_id] = States.S_START
        start(c.message)
#-------------------------------------------------------
        
#Funzione Non legata a decoratori per mostrare i corsi
def mostraCorsi(message):
    chat_id = message.chat.id
    
    #Crea il markup
    markup = types.InlineKeyboardMarkup()

    #Salva tutti i corsi in una variabile.
    result = db.getCorsi()

    #Stampa tutti i corsi e aggiunge un opzione di ritorno al menu precedente
    for riga in result:
        btn = types.InlineKeyboardButton(""+str(riga[2])+" - "+str(riga[3])+" - "+str(riga[4]), callback_data='opz'+str(riga[0]))
        markup.add(btn)
    btn = types.InlineKeyboardButton("Torna al menu", callback_data='opzEsc')
    markup.add(btn)

    bot.send_message(chat_id, "Scegli un corso:", reply_markup=markup)

#Handler per i bottoni dei corsi.
@bot.callback_query_handler(func=lambda call: call.data.startswith('opz') and not call.data in ['op1', 'op2', 'op3'])
def corsi_buttons_handler(c):
    chat_id = c.message.chat.id
    corso_id = c.data[3:]  #Estre l'ID del corso


    if corso_id != "Esc":
        # Crea il markup per la conferma
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("Sì", callback_data='confirm_yes_' + corso_id)
        btn_no = types.InlineKeyboardButton("No", callback_data='confirm_no')
        markup.add(btn_yes, btn_no)

        bot.send_message(chat_id, "Vuoi confermare la prenotazione per il corso con ID: " + str(corso_id) + "?", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Operazione annullata.")
        mostraMenu(c.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def conferma_prenotazione_corso(c):
    chat_id = c.message.chat.id

    #Metodo per recuperare corsoID senza doverlo prendere di nuovo dal DB
    response = c.data.split('_')[1]
    corso_id = c.data.split('_')[2] if len(c.data.split('_')) > 2 else None

    if response == "yes":
        #Verifica dei posti disponibili
        if db.getPostiCorso(corso_id) == 0:
            bot.send_message(chat_id, "Non ci sono posti per il corso con ID: " + str(corso_id))
        #Verifica prenotazione già effettuata
        elif db.prenotazioneGiaEffettuata(user_data[chat_id]["matricola"], corso_id) == True:
            bot.send_message(chat_id, "Hai già effettuato una prenotazione per il corso con ID: " + str(corso_id))
        else:
            # Sottrae dal counter dei posti rimanenti 1 posto e prenota il corso
            db.eliminaPostoCorso(corso_id)
            db.prenotaPostoCorso(user_data[chat_id]["matricola"], corso_id)
            bot.send_message(chat_id, "Hai confermato la prenotazione per il corso con ID: " + str(corso_id))
    elif response == "no":
        bot.send_message(chat_id, "Operazione annullata.")

    mostraMenu(c.message)



#Funzione non legata a decoratori per mostrare le prenotazioni di una determinata matricola
def mostraPrenotazioni(message):
    chat_id = message.chat.id
    matricola = user_data[chat_id]["matricola"]

    #Crea il markup
    markup = types.InlineKeyboardMarkup()

    #Salva tutti i corsi in una variabile.
    result = db.getPrenotazioni(matricola)

    #Stampa tutti i corsi e aggiunge un opzione di ritorno al menu precedente
    for riga in result:
        btn = types.InlineKeyboardButton("Prenotazione con ID: "+str(riga[0])+". Per il corso di: "+str(db.getCorsoFromPrenotazione(riga[0]))+", in data: "+str(riga[3])+". Effettuata il "+str(riga[4]), callback_data='prz'+str(riga[0]))
        markup.add(btn)
    btn = types.InlineKeyboardButton("Torna al menu", callback_data='opzEsc')
    markup.add(btn)
    bot.send_message(chat_id, "Scegli una prenotazione se la vuoi eliminare:", reply_markup=markup)

#Handler per i bottoni delle prenotazioni.
@bot.callback_query_handler(func=lambda call: call.data.startswith('prz') and not call.data in ['op1', 'op2', 'op3'])
def prenotazioni_buttons_handler(c):
    chat_id = c.message.chat.id
    prenotazione_id = c.data[3:]  #Estre l'ID della prenotazione


    if prenotazione_id != "Esc":
        # Crea il markup per la conferma
        markup = types.InlineKeyboardMarkup()
        btn_yes = types.InlineKeyboardButton("Sì", callback_data='confirmD_yes_' + prenotazione_id)
        btn_no = types.InlineKeyboardButton("No", callback_data='confirmD_no')
        markup.add(btn_yes, btn_no)

        bot.send_message(chat_id, "Vuoi confermare la rimozione della tua prenotazione con ID: " + str(prenotazione_id) + "?", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Hai conservato la prenotazione.")
        mostraMenu(c.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirmD_'))
def conferma_prenotazione_corso(c):
    chat_id = c.message.chat.id

    #Metodo per recuperare corsoID senza doverlo prendere di nuovo dal DB
    response = c.data.split('_')[1]
    prenotazione_id = c.data.split('_')[2] if len(c.data.split('_')) > 2 else None

    if response == "yes":
        #Aggiunge un posto data l'eliminazione della prenotazione
        db.fixPostiCorsoFromDeletePrenotazione(prenotazione_id)
        #Elimina la tupla con id prenotazione come da passaggio
        db.deletePrenotazione(prenotazione_id)
        bot.send_message(chat_id, "Hai confermato la cancellazione della prenotazione con ID: " + str(prenotazione_id))
    elif response == "no":
        bot.send_message(chat_id, "Hai conservato la prenotazione.")

    mostraMenu(c.message)

#Ultima riga che permette l'ascolto continuo dei messaggi.
bot.infinity_polling()