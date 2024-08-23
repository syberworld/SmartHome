# Librerie

## Comunicazioni (Communicatons.py)
### WiFi - Gestione dell'interfaccia di rete
> WiFi(proxy=False) - Instanzia la classe e connette il dispositivo alla rete
> - proxy - (boolean) - True si connette alla rete locale WiFi (modalità Proxy), False non si connette e attiva l'interfaccia di rete (modalità Client)

`get_mac()` - (bytearray) Restituisce il Mac Address delle periferica in formato bytearray

`print_mac()` - Stampa a video il Mac Address in formato user friendly

### DSS (Data Sender System) - Funzioni di basso livello per le comunicazioni con protocollo EspNow
> Dss(fn_callback) - Instanzia la classe e avvia il demone che si occupa di rimanere in attesa di dati da altri dispositivi
> - fn_callback - (function) Funzione esterna che viene avviata quando viene ricevuto un messaggio completo

`send_message(peer, message)` - Invia ad un altro dispositivo il messaggio
- peer - (bytearray) Mac Adress del destinatario
 
- message - (string) Messaggio testuale da inviare

`send_data(peer, data)` - Invia un pacchetto di dati ad un altro dispositivo
- peer - (bytearray) Mac Adress del destinatario 
  
- data - (dict) Pacchetto di dati organizzati come dizionario

## Archivio Dati (DataStorage.py)
### DSP (Data Service Provider) - Funzioni di gestione dell'archivio dati istantanei
Immagazzina e gestisce i dati del dispositivo
> Dsp() - Instanzia l'archivio dati che sarà inizialmente vuoto

`store` - (dict) Contiene i dati del dispositivo

`read(path)` - (dict, int, str) Legge il dato contenuto, anche nidificato, nella posizione richiesta
- path - (string) Percorso del dato da leggere separato da punti
  > Esempi:<br />
  > read("Sensori\Temperatura\Value") restituisce un intero contenuto nella posizione richiesta<br />
  > read("Sensori\Temperatura") restituisce un dict del tipo {'Value': 10, 'Unita':"°C"}

`write(path, value)` - Scrive il dato nella posizione richiesta
- path - (string) Percorso del dato da leggere separato da punti
- value - (dict, string, int) Dato da inserire nel data storage
  > Esempi:<br />
  > write("Sensori\Temperatura\Value", 10) Scrive il valore intero nella specifica posizione<br />
  >  write("Sensori\Temperatura", {'Value': 10, 'Unita':"°C"}) Scrive il dato complesso nella specifica posizione

`delete(path)` - Elimina il dato presente nella posizione richiesta
- path - (string) Percorso del dato da leggere separato da punti
