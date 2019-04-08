import hashlib
from socketserver import ThreadingUDPServer
from socketserver import DatagramRequestHandler

from pysip.log import logger


class RTPProxyEmulator(ThreadingUDPServer):
    def run(self):
        host, port = self.server_address
        logger.info(f'RTPProxy Emulator listen on {host}:{str(port)}.')
        try:
            self.serve_forever()

        except KeyboardInterrupt:
            logger.warn('RTPProxy Emulator manually closed.')


class RTPProxyRequestHandler(DatagramRequestHandler):
    def handle(self):
        self.hasher = hashlib.md5()
        datagram = self.rfile.readline().strip()
        host, port = self.client_address
        str_datagram = datagram.decode('utf-8') 
        self.hasher.update(datagram)
        unique_id = self.hasher.hexdigest()
        logger.debug('Information received: {}'.format(str_datagram))
        logger.debug('Information sent: {}'.format(str_datagram.upper()))
        self.wfile.write(str_datagram.upper().encode('utf-8'))
        logger.info('Receiving tests of {}:{} - [{}]'.format(host, port, unique_id))
