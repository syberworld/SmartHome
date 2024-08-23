# Librerie

## Comunicazioni (Communicatons.py)
### DSS (Data Sender System) - Funzioni di basso livello per le comunicazioni con protocollo EspNow
> Dss(fn_callback) - Instanzia la classe e avvia il demone che si occupa di rimanere in attesa di dati da altri dispositivi
> - fn_callback - (function) Funzione esterna che viene avviata quando viene ricevuto un messaggio completo

`get_mac()` - Restituisce il Mac Address delle periferica in formato bytearray

`print_mac()` - Stampa a video il Mac Address in formato user friendly

`send_message(peer, message)` - Invia ad un altro dispositivo il messaggio
  - peer - (bytearray) Mac Adress del destinatario
 
  - message - (string) Messaggio testuale da inviare

`send_data(peer, data)` - Invia un pacchetto di dati ad un altro dispositivo
  - peer - (bytearray) Mac Adress del destinatario 
  
  - data - (dict) Pacchetto di dati organizzati come dizionario
