from time import time
from random import choices
from string import ascii_lowercase

from pysip.log import logger


def average(iterable):
    value = sum(iterable) / len(iterable)
    return '{:.5f}'.format(value)

def minimal(iterable):
    value = min(iterable)
    return '{:.5f}'.format(value)

def maximum(iterable):
    value = max(iterable)
    return '{:.5f}'.format(value)

def  send_loop(socket, size, loop):
    status = list()
    durations = list()

    for i in range(loop):
        try:
            data = ''.join(choices(ascii_lowercase, k=(size - 44)))
            start = time()
            logger.debug(f'Data sent: {data}')
            socket.send(data.encode())
            response = socket.recv(4096).decode('ASCII')
            end = time()
            logger.debug(f'Data recived: {response}')
            status.append(data.upper() == response)
            durations.append(end - start)
        
        except ConnectionRefusedError:
            status.append(False)
            durations.append(5)

    return status, durations