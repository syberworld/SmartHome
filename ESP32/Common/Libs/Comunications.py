import network
import espnow
import json


class Dss():

    def __init__(self, fn_callback):
        self.fn_callback = fn_callback
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.esp = espnow.ESPNow()
        self.esp.active(True)
        self.messages = {}
        self.esp.irq(self._demon)

    def get_mac(self):
        if self.wlan.active():
            return self.wlan.config("mac")
        else:
            return False

    def print_mac(self):
        if self.wlan.active():
            mac_address = self.wlan.config("mac")
            print("Device MAC Address:", ":".join(["{:02X}".format(byte) for byte in mac_address]))
        else:
            print("Wi-Fi is not active.")

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
                self.fn_callback(mac, self.messages[mac])
                del(self.messages[mac])

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
