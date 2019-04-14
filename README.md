# IPSLA

VoIP test tool to check VoIP circuits


## How to install python 3.7

- install dependencies
```bash
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev
```

- Download source code and unzip
```bash
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.7.2/Python-3.7.2.tgz
sudo tar xzf Python-3.7.2.tgz
```

- Compile
```bash
cd Python-3.7.2
sudo ./configure --enable-optimizations
sudo make altinstall
```

- Get PIP
```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.7 get-pip.py
```

## How to install and use CLI
```bash
python3.7 -m pip install -r requirements.txt
python3.7 setup.py install
...
pysipctl --help
```