from os import path
from time import time
from hashlib import md5

from jinja2 import Environment, FileSystemLoader


here = path.abspath(path.dirname(__file__))


class Message:
    def __init__(self, name, **kwargs):
        self.loader = FileSystemLoader(path.join(here, 'templates'))
        self.env = Environment(loader=self.loader)
        self.name = name
        self.params = kwargs
    
    @staticmethod
    def make_hash(text):
        hasher = md5()
        hasher.update(text.encode('utf-8'))
        return hasher.hexdigest()

    @property
    def render(self):
        if  path.exists(path.join(here, 'templates', self.name + '.txt')):
            file = self.name + '.txt'
            template = self.env.get_template(file)
            message = template.render(self.params)
            return message.encode().replace(b'\n', b'\r\n')

        else:
            raise FileNotFoundError('Message not Found')

    @render.setter
    def render(self):
        raise AttributeError('This message is not editable.')


def parse_header(text):
    length = len(text.split(':')) - 1
    result = text.split(':', 1) if length else ['title', text]
    chave, valor = result
    return (chave.strip(), valor.strip())
