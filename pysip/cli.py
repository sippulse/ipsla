import socket
import logging
from time import time
from random import random
from functools import reduce

import click
from pynat import get_ip_info

from pysip.log import logger
from pysip.messages import Message, parse_header
from pysip.utils import send_loop, average, minimal, maximum
from pysip.socketserver import RTPProxyEmulator, RTPProxyRequestHandler

@click.group()
def cli():
    '''
    Função que representa a CLI em si.
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

@server.command('rtp', help='Performs the connection test for RTP Proxy machines.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, required=True, help='Port of the test.')
def rtp(host, port):
        address = (host, port)
        with RTPProxyEmulator(address, RTPProxyRequestHandler) as server:
                try:
                        logger.info(f'RTPProxy Emulator listen on {host}:{str(port)}.')
                        server.serve_forever()

                except KeyboardInterrupt:
                        logger.warn('RTPProxy Emulator manually closed.')

@client.command('rtp', help='Performs the connection test for RTP Proxy machines.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, required=True, help='Port of the test.')
@click.option('--loops', type=int, default=1000, help='Number of packets to be sent..')
@click.option('--size', type=int, default=1024, help='Size of the packet to be sent (in bytes).')
def rtp(host, port, size, loops):
        address = (host, port)
        logger.info('Performing RTP Proxy test.')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                client.settimeout(5)
                client.connect(address)
                
                status, durations = send_loop(client, size, loops)
                jitter = max(durations) - min(durations)

                if all(status):
                        logger.info('Test completed successfully.')
                        logger.info(f'Package size used: {str(size)} bytes')
                        logger.info(f'Total of packages sent: {str(loops)}')
                        logger.info(f'Average of latency: {average(durations)} seconds.')
                        logger.info(f'Latency peak: {maximum(durations)} seconds.')
                        logger.info(f'Latency lowest: {minimal(durations)} seconds.')
                        logger.info('Jitter: {:.5f} seconds.'.format(jitter))

                else:
                        logger.warning('Test finished with failure.')

@client.command('nat', help='Identifies the type of NAT used on the network.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--port', type=int, default=3478, help='Port of the test.')
def nat(host, port):
        topology, ext_ip, ext_port, int_ip = get_ip_info(
                include_internal=True, stun_host=host, stun_port=port
        )
        logger.info(f'Topology tipe: {topology}')
        logger.debug(f'Internal interface used: {int_ip}')
        logger.debug(f'External address: {ext_ip}:{ext_port}')


@client.command('alg', help='Performs the ALG test with the host informed.')
@click.option('--host', type=str, required=True, help='Host of the test.')
@click.option('--username', type=str, required=True, help='Username of the test.')
@click.option('--domain', type=str, required=True, help='Domain of the test.')
@click.option('--port', type=int, default=5060, help='Port of the test.')
def aug(host, port, username, domain):
    logger.info('Performing ALG test.')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as interface:
        interface.settimeout(5)
        destiny_address = (host, port)
        logger.info(f'Destiny IP: {host}')
        logger.info(f'Destiny Port: {port}')
        interface.connect(destiny_address) 
        in_host, in_port = interface.getsockname()
        logger.info(f'Internal IP used: {in_host}')
        logger.info(f'Internal selected port: {in_port}')
        callid = Message.make_hash(str(time() * random()))
        to_tag = Message.make_hash(str(time() * random()))
        branch = Message.make_hash(str(time() * random()))
        logger.debug(f'Call-ID generated for the package: {callid}')
        logger.debug(f'To-Tag generated for the package: {to_tag}')
        logger.debug(f'Branch-Tag generated for the package: {branch}')
        logger.debug('Generating INVITE that will be forwarded to the Host.')
        message = Message('invite', **{
                'address': {'ip': in_host, 'port': in_port },
                'branch': branch,
                'from': {
                        'user': username,
                        'domain': domain,
                        'tag':  to_tag
                },
                'callid': callid
        })
        try:
                interface.send(message.render)
                response = interface.recv(4096).decode('ASCII')
                resp_list = [v for v in response.split('\r\n') if v]
                result = dict(parse_header(value) for value in resp_list)
                logger.info(f'Response title: {result["title"]}')
                logger.debug(f'Call-ID response: {result["Call-ID"]}')
                logger.debug(f'Response source server: {result["Server"]}')
                _, title = result["title"].split('200')

                if title.strip() == 'OK':
                        logger.info('ALG test completed successfully.')

                else:
                        logger.warn('Router with ALG detected.')

        except KeyError:
                logger.error('Could not parse the response.')

        except socket.timeout:
                logger.error('Connection timeout with SipProxy.')
