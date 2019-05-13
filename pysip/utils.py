from time import time
from random import choices
from string import ascii_lowercase

from pysip.log import logger


def percentage(iterable, value):
    total = len(iterable)
    counts = iterable.count(value)
    return counts / total * 100


def mos(status):
    ie = 0
    bpl = 10
    rate = 64000
    ppl = percentage(status, False)
    ie_eff = ie + (95.0 - ie) * ppl / (ppl + bpl)
    rlq = 93.2 - ie_eff
    mos = 10 * (1 + rlq * 0.035 + rlq * (100 - rlq) * (rlq - 60) * 0.000007)/10
    return mos


def average(iterable):
    value = sum(iterable) / len(iterable)
    return value


def  send_loop(socket, size, loop):
    status = list()
    durations = list()

    for i in range(loop):
        try:
            data = ''.join(choices(ascii_lowercase, k=(size - 44)))
            start = time()
            logger.debug('Data sent: {}'.format(data))
            socket.send(data.encode())
            response = socket.recv(4096).decode('ASCII')
            end = time()
            logger.debug('Data recived: {}'.format(response))
            status.append(data.upper() == response)
            durations.append(end - start)
        
        except (ConnectionRefusedError, OSError):
            status.append(False)
            durations.append(5)

    return status, durations
