
# Xray-User-Management

A simple program to manage xray users.


## Installation

Install Xray-User-Management with the following steps:

1- Clone the project
```bash
git clone the-project
```

2- Download xray core and unzip it and move the xray and geosite.dat and geoip.dat to the Xray-User-Management directory

3- go to Xray-User-Management directory
```bash
cd Xray-User-Management
```

4- make xray and run.sh executable
```bash
chmod +x xray run.sh
```

5- edit the 'config.json' file for the traffic protocol.
Note: DO NOT alter any other section except this section:
```json
            "port": 443,
            "protocol": "vless",
            "settings": {
                "udp": false,
                "clients": [
                ],
                "decryption": "none",
                "allowTransparent": false
            },
```

6- execute the 'run.sh'
```bash
./run.sh
```

## Usage/Examples

1- You should only add a user with 'add_user_to_config_file.py' python code

for help:
```bash
python3 add_user_to_config_file.py -h
```

2- you should can delete a user with 'del_user_from_config_file.py' python code

for help:
```bash
python del_user_from_config_file.py -h
```


