import network
import espnow
import json
import time
from micropython import const

class Wifi():
    def __init__(self, proxy=False):
        self.sta, ap = self._wifi_reset()
        if proxy:
            self.sta.connect('ssid', 'password')
            while not self.sta.isconnected():
                time.sleep(0.1)
            self.sta.config(pm=self.sta.PM_NONE)
            print("Wlan attiva")
            print("  Ip      : " + str(self.sta.ifconfig()[0]))
            print("  Subnet  : " + str(self.sta.ifconfig()[1]))
            print("  Gateway : " + str(self.sta.ifconfig()[2]))
            print("  Dns     : " + str(self.sta.ifconfig()[3]))
            mac_address = self.sta.config("mac")
            print("  Device MAC Address:", ":".join(["{:02X}".format(byte) for byte in mac_address]))
            print("Proxy running on channel:", self.sta.config("channel"))
        else:
            self.sta.config(channel=6)
            print("Client running on WiFi channel:", self.sta.config("channel"))

        '''
        self.wlan = network.WLAN(network.STA_IF)
        if not self.wlan.isconnected():
            print('Connessione alla Wlan...')
            self.wlan.active(True)
            self.wlan.connect('iliadbox-60ADCB', 'LiNkWiFi.01')
            while not self.wlan.isconnected():
                pass
        print("Wlan attiva")
        print("  Ip      : " + str(self.wlan.ifconfig()[0]))
        print("  Subnet  : " + str(self.wlan.ifconfig()[1]))
        print("  Gateway : " + str(self.wlan.ifconfig()[2]))
        print("  Dns     : " + str(self.wlan.ifconfig()[3]))
        '''

    def get_mac(self):
        if self.sta.active():
            return self.sta.config("mac")
        else:
            return False

    def print_mac(self):
        if self.sta.active():
            mac_address = self.sta.config("mac")
            print("Device MAC Address:", ":".join(["{:02X}".format(byte) for byte in mac_address]))
        else:
            print("Wi-Fi is not active.")

    def _wifi_reset(self):
        sta = network.WLAN(network.STA_IF)
        sta.active(False)
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        sta.active(True)
        while not sta.active():
            time.sleep(0.1)
        sta.disconnect()  # For ESP8266
        while sta.isconnected():
            time.sleep(0.1)
        return sta, ap

class Dss(): # Data Sender System

    def __init__(self, fn_callback):
        self.fn_callback = fn_callback
        #self.wlan = network.WLAN(network.STA_IF)
        #self.wlan.active(True)
        self.esp = espnow.ESPNow()
        self.esp.active(True)
        self.messages = {}
        self.esp.irq(self._demon)

    def send_message(self, peer, message):
        try:
            self.esp.add_peer(peer)
        except:
            pass
        blocks = self._split(message)
        for block in blocks:
            self.esp.send(peer, block)
        self.esp.send(peer, "[END]")

    def send_data(self, peer, data):
        data = json.dumps(data)
        self.send_message(peer, data)

    def _demon(self, esp):
        while True:
            mac, msg = esp.irecv(0)
            if mac is None:
                return
            message = msg.decode("utf-8")
            if message != "[END]":
                self._uncut_message(mac, message)
            else:
                m = self._decode(self.messages[mac])
                del (self.messages[mac])
                self.fn_callback(mac, m)

    def _split(self, message, lengh=250, encoding='utf-8'):
        blocks = []
        idx = 0
        while idx < len(message):
            len_block = min(lengh, len(message[idx:]))
            bloc_bytes = message[idx:idx + len_block].encode(encoding)
            len_tot = len(bloc_bytes)
            blocks.append(bloc_bytes.decode(encoding))
            idx += len_tot
        return blocks

    def _uncut_message(self, peer, message):
        if peer in self.messages:
            self.messages[peer] = str(self.messages[peer]) + message
        else:
            self.messages[peer] = message

    def _decode(self, message):
        return json.loads(message)


class Exchange():
    TYPE_REQUEST_DATA = const(0)    # Richiede dato
    TYPE_DATA = const(1)            # Dato RAW
    TYPE_REQUEST_SYNCRO = const(2)  # Richiede dato
    TYPE_SYNCRO = const(3)          # Dato RAW
    TYPE_COMMAND = const(9)         # Comando generico

    def __init__(self, dsp, dss):
        self.dsp = dsp
        self.dss = dss

    # Data
    def request_data(self, peer, path):
        message = {'Type': self.TYPE_REQUEST_DATA, 'Path': path}
        self.dss.send_data(peer, message)

    def send_data(self, peer, path):
        data = self.dsp.read(path)
        message = {'Type': self.TYPE_DATA, 'Data': data}
        self.dss.send_data(peer, message)

    # Command
    def command(self, peer, command, params):
        message = {'Type': self.TYPE_COMMAND, 'Command': command, 'Params': params}
        self.dss.send_data(peer, message)

    # Control
    def request_syncro(self, peer):
        message = {'Type': self.TYPE_REQUEST_SYNCRO}
        self.dss.send_data(peer, message)

    def send_syncro(self, peer):
        message = {'Type': self.TYPE_SYNCRO, "Time": time.time()}
        self.dss.send_data(peer, message)





    '''
    def keys_read(self):
        # Carica la tabella
        with open("data/keys.json", mode="r", encoding="utf-8") as read_file:
            if read_file: keys = json.load(read_file)
            else: keys = {}
        # Aggiunge i peer all'ESP
        for peer in keys:
            self.esp.add_peer(peer)
        return keys

    def keys_write(self):
        with open("data/keys.json", mode="w", encoding="utf-8") as write_file:
            json.dump(self._keys, write_file)

    def keys_add(self, host, key):
        self._keys[host] = key
        self.esp.add_peer(host)
        self.keys_write()

    def key_create(self, size=32):
        return uos.urandom(size)

    def send_message(self, host, message, crypt=True):
        #Invia il messagio all'host indicato
        if crypt:
            message = self.FLAG_CRYPT + self._encrypt(message, self._keys[host][1])
        else:
            message = self.FLAG_PLAIN + message
        # Invia il messaggio
        self.esp.send(host, message, True)

    def send_data(self, host, data, crypt=True):
        #Infia una struttura dati all'host indicato
        serial = json.dumps(data)
        self.send_message(host, serial, crypt)

    def _encrypt(self, message, key):
        # Cripta il messaggio con la chiave passata 
        crypto = cryptolib.aes(key, self.MODE_CBC, self.iv)
        pad = self.BLOCK_SIZE - len(message) % self.BLOCK_SIZE
        plaintext = message + " " * pad
        return crypto.encrypt(plaintext)

    def _decypt(self, message, key):
        # Decripta il messaggio con la chiave passata
        crypto = cryptolib.aes(key, self.MODE_CBC, self.iv)
        decrypted = crypto.decrypt(message)
        return decrypted

    def _demon(self, ):
        print("Servizio avviato: Server EspNow")
        while True:
            host, msg = self.esp.recv()
            if msg:  # msg == None if timeout in recv()
                self._recive(host, msg)

    def _recive(self, host, message):
        if message[0] == self.FLAG_CRYPT:
            message = self._decypt(message[1:])
        elif message[0] == self.FLAG_PLAIN:
            message = message[1:]
        self.fn_callback(host, message)

    def read_crypt(self, host, path):
        key = self._keys[host]
        plaintext = json.dumps((path))
        encrypted = self._encrypt(plaintext, key)
        self.send(host, self.CMD_READ_CRYPT + encrypted)

    def write_crypt(self, host, path, value):
        key = self._keys[host]
        plaintext = json.dumps((path, value))
        encrypted = self._encrypt(plaintext, key)
        self.send(host, self.CMD_WRITE_CRYPT + encrypted)

    def read_decrypt(self, host, message):
        key = self._keys[host]
        msg = json.loads(self._decypt(message, key))
        self._dsp.read(msg[0])

    def write_decrypt(self, host, message):
        key = self._keys[host]
        msg = json.loads(self._decypt(message, key))
        self._dsp.write(msg[0], msg[1])

    def _recive(self, host, message):
        if message[0] == self.CMD_READ_CRYPT:
            self.read_decrypt(host, message)
        elif message[0] == self.CMD_WRITE_CRYPT:
            self.write_decrypt(host, message)
        else:
            pass





    def read(self, path):
        path = path.split(".")
        data = self.store
        for i in range(0, len(path)):
            try:
                data = data[path[i]]
            except():
                return False
        return data

    def write(self, path, value):
        path = path.split(".")
        data = self.store
        for i in range(0, len(path)-1):
            data = data.setdefault(path[i], {})
        data[path[-1]] = value

    def delete(self, path):
        paths = path.split(".")
        del self.read(path.rsplit('.', 1)[0])[paths[-1]]

    def send(self, addr, path):
        plaintext = json.dumps(self.read(path))
        pad = self.BLOCK_SIZE - len(plaintext) % self.BLOCK_SIZE
        plaintext = plaintext + " " * pad
        encrypted = self.crypto_remote.encrypt(plaintext)
        print('AES-ECB encrypted:', encrypted)
        #----------
        decrypted = self.crypto_local.decrypt(encrypted)
        print('AES-ECB decrypted:', decrypted)
        new_dic = json.loads(decrypted)
        print(new_dic)

        #message = self.crypto_local.encrypt(el)
        #print(self.crypto_local.decrypt(message)) # Test Only
        # apri socket
        #invia messaggio
        pass

    def recive(self, buffer):
        # Nell'altra macchina
        decrypted = self.crypto_local.decrypt(buffer)
        print('AES-ECB decrypted:', decrypted)
        new_dic = json.loads(decrypted)
        print(new_dic)
'''