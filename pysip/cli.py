import click
import socket
import logging
from time import time
from random import random
from pprint import pprint

from pysip.log import logger
from pysip.messages import Message, parse_header


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
    logger.debug('DEBUG mode enabled.')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
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
