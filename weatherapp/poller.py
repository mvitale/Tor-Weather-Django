from TorCtl import TorCtl
import socket
import weather.config

class Poller(TorCtl.EventHandler):

def main():
    ctrl_host = "127.0.0.1"
    ctrl_port = 9051
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ctrl_host, ctrl_port))

    ctrl = TorCtl.Connection(sock)
    ctrl.authenticate(config.authenticator)
    poll = Poller(ctrl)

