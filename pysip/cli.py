import socket
import logging
import hashlib
from time import time
from random import random
from functools import reduce

import click

from pysip.log import logger
from pysip.utils import send_loop, average, mos, percentage
from pysip.messages import Message, parse_header
from pysip.socketserver import RTPProxyEmulator, RTPProxyRequestHandler

@click.group()
def cli():
    '''
    VoIP test tool.
    '''
    ...


@cli.group()
@click.option('--debug', type=bool, help='Enable debug mode.')
def server(debug):
    '''
    Command that starts the application in SERVER mode.
    '''
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug('DEBUG mode enabled.')
    logger.info('Application started in SERVER mode.')


@cli.group()
@click.option('--debug', type=bool, help='Enable debug mode.')
def client(debug):
    '''
    Command that starts the application in CLIENT mode.
    '''
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.debug('DEBUG mode enabled.')
    logger.info('Application started in CLIENT mode.')


@server.command('rtp', help='Performs the connection test for RTP performance.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, required=True, help='Port of the test.')
def rtp(host, port):
        address = (host, port)
        with RTPProxyEmulator(address, RTPProxyRequestHandler) as server:
                try:
                        logger.info('RTP emulator listen on {}:{}.'.format(host, port))
                        server.serve_forever()

                except KeyboardInterrupt:
                        logger.warn('RTP Emulator manually closed.')


@client.command('rtp', help='Performs the connection test for RTP machines.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, required=True, help='Port of the test.')
@click.option('--loops', type=int, default=1000, help='Number of packets to be sent.')
@click.option('--size', type=int, default=1024, help='Size of the packet to be sent (in bytes).')
def rtp(host, port, size, loops):
        address = (host, port)
        logger.info('Performing RTP test.')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                client.settimeout(5)
                client.connect(address)
                
                status, durations = send_loop(client, size, loops)
                jitter = max(durations) - min(durations)

                if all(status):
                        logger.info('Test completed successfully.')
                        logger.info('Package size used: {:d} bytes'.format(size))
                        logger.info('Total of packages sent: {:d}'.format(loops))
                        logger.info('Average of latency: {:.2f} miliseconds.'.format(average(durations)/2*1000))
                        logger.info('Latency peak: {:.2f} miliseconds.'.format(max(durations)/2*1000))
                        logger.info('Latency lowest: {:.2f} miliseconds.'.format(min(durations)/2*1000))
                        logger.info('Jitter: {:.2f} miliseconds.'.format(jitter*1000))
                        logger.info('Packet Loss {:.2f}'.format(percentage(status,False)))
                        logger.info('MOS: {:.2f}'.format(mos(status)))
                else:
                        logger.warning('Test finished with failure.')


@client.command('alg', help='Performs the ALG test with the host informed.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, default=5060, help='Port of the test.')
@click.option('--test', type=int, default=7, help='Type of tests.')
def aug(host, port,test):
    logger.info('Performing ALG test.')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as interface:
        interface.settimeout(5)
        destiny_address = (host, port)
        logger.info('Destiny IP: {}'.format(host))
        logger.info('Destiny Port: {}'.format(port))
        interface.connect(destiny_address) 
        in_host, in_port = interface.getsockname()
        ip_hash = hashlib.md5(in_host.encode())
        logger.info('Internal IP used: {}'.format(in_host))
        logger.info('Internal selected port: {}'.format(in_port))
        callid = Message.make_hash(str(time() * random()))
        to_tag = Message.make_hash(str(time() * random()))
        branch = Message.make_hash(str(time() * random()))
        logger.debug('Call-ID generated for the package: {}'.format(callid))
        logger.debug('To-Tag generated for the package: {}'.format(to_tag))
        logger.debug('Branch-Tag generated for the package: {}'.format(branch))
        logger.debug('Generating INVITE that will be forwarded to the Host.')
        message = Message('invite',
                          callid=callid,
                          branch=branch,
                          test=test,
                          address={'ip': in_host, 'port': in_port },
                          iphash={ 'hash': ip_hash.hexdigest() }, 
                          sip_from={'user': "algtest", 'domain': in_host, 'tag':  to_tag})

        try:
                interface.send(message.render)
                response = interface.recv(4096).decode('ASCII')
                resp_list = [v for v in response.split('\r\n') if v]
                result = dict(parse_header(value) for value in resp_list)
                logger.info('Response title: {}'.format(result["title"]))
                logger.debug('Call-ID response: {}'.format(result["Call-ID"]))
                logger.debug('Response source server: {}'.format(result["Server"]))
                _, title = result["title"].split('200')

                if title.strip() == 'OK':
                        logger.info('No ALG detected')

                else:
                        logger.warn('Router with ALG detected.')

        except KeyError:
                logger.error('Could not parse the response.')

        except socket.timeout:
                logger.error('Connection timeout with SipProxy.')
