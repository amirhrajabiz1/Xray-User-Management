
# Xray-User-Management

A simple program to manage xray users.


## Installation

Install Xray-User-Management with the following steps:

1- Clone this project
```bash
git clone https://github.com/amirhrajabiz1/Xray-User-Management.git
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

5- edit the 'conf/inbound.json' for inbound protocols you want to use.
`Note`: Make sure the client is empty and you should use 'add_user_to_config_file.py' to add user to the 'conf/inbound.json'.

6- execute the 'run.sh' with root privilege
```bash
sudo ./run.sh
```

## Usage

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

## Examples

1- This command will create a user, amir, in 'conf/inbound.json' with a maximum bandwidth of 100GB for 30 days. Additionally, only one different IP address can use this account simultaneously:
```bash
sudo python3 add_user_to_config_file.py -u amir -c conf/inbound.json -l 100G -d 30 -s 1
```

2- Now, assume user 'amir' consumes 100GB with this account. In this case, amir's ID will be removed from the 'conf/inbound.json', and the following log will be recorded in 'reasonremove.log':
`2024-01-28 15:18:29 user 'amir' removed because of quota_out.`

3- After 30 days, amir's ID will be removed from the 'conf/inbound.json', and the following log will be recorded in 'reasonremove.log':
`2025-10-10 10:10:18 user 'amir' removed because of time_out.`

4- If amir connects with more than one connection (source IP address) to this account concurrently, amir's ID will be removed from the 'conf/inbound.json', and the following log will be recorded in 'reasonremove.log':
`2025-10-10 10:12:49 user 'amir' removed because of CC_violation.`

5- If you choose to delete amir manually, in this case, amir's ID will be removed from the 'conf/inbound.json', and the following log will be recorded in 'reasonremove.log':
`2024-01-30 14:46:28 user 'amir' removed manually.`
`Note`: use switch `-f` if you want to delete the user statistics and information completely.

6- Now, if you want to create the user 'amir' again with the previous ID, you can enter this:
```bash
sudo python3 add_user_to_config_file.py -u amir -c conf/inbound.json -l 100G -d 30 -s 1 -f soft
```

7- If you want to create the user 'amir' with a new ID, you can enter this:
```bash
sudo python3 add_user_to_config_file.py -u amir -c conf/inbound.json -l 100G -d 30 -s 1 -f hard
```

## Files And Directories
`conf/inbound.json`: You put your inbound configs here.
`users/user/Statistics/`: You find user statistics here.
`users/user/user.json`: You find user information here.
`reasonremove.log`: You find logs of why a user removed from 'conf/inbound.json'.







