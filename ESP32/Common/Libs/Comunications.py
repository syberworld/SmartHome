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
