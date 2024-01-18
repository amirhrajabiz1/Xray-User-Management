import math
import json
import subprocess
import socket
import os
from datetime import datetime, timedelta
from pathlib import Path


LOG_PATH = './users.log'



def get_date_range(days: int) -> str:
    """
  This function takes the number of days as input and returns a string containing the start and end date separated by a hyphen.

  Args:
    days: The number of days from today.

  Returns:
    A string containing the start and end date separated by a hyphen.
    """
    today = datetime.today()
    end_date = today + timedelta(days=days)
    start_date_str = today.strftime("%Y%m%d")
    end_date_str = end_date.strftime("%Y%m%d")
    return f"{start_date_str}-{end_date_str}"


def convert_to_bytes(size_str):
    """
    Converts a given size string (e.g., '2GB', '2G', '500MB') to its equivalent in bytes.

    The function supports the following units:
    B, KB, MB, GB, TB, PB, EB, ZB, YB

    Parameters:
    size_str (str): The size string to be converted.

    Returns:
    int: The equivalent size in bytes.
    """

    # Define the conversion factors for each uniti
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    # add 'B' if the input has just a numeric part.
    if size_str[-1].isdigit():
        size_str += 'B'

    # Extract the numeric part and the unit part from the input string
    if size_str[-2].isdigit(): # Handle cases like '2GB' and '2G'
        num, unit = size_str[:-1], size_str[-1]
        # Append 'B' if the unit is a single letter (e.g., 'G' for 'GB')
        unit += 'B' if unit != 'B' else ''
    else: # Handle cases like '2GB' where the unit is two characters
        num, unit = size_str[:-2], size_str[-2:]

    # Convert the numeric part to float and multiply by the corresponding unit factor
    try:
        num = float(num)
        return int(num * (1024**units.index(unit)))
    except ValueError:
        raise ValueError("invalid size format or unsupported unit")


def convert_size(size_bytes):
    """
    Take byte number and return human readable form of it.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s%s" % (s, size_name[i])


def create_user(name: str, uuid=None) -> dict:
    """
    get a name and return a dict user.
    """
    user = dict()
    if not uuid:
    	uuid = subprocess.run('./xray uuid', shell=True, capture_output=True, text=True).stdout.strip()
    user['id'] = uuid
    user['alterId'] = 0
    user['email'] = name
    user['flow'] = ''
    user['level'] = 0
    return user

def get_ip():
    # Attempt to connect to an external host to determine the external IP
    try:
        # Use a dummy socket to connect to an external server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to Google's public DNS server
            s.connect(("8.8.8.8", 80))
            # Get the socket's own address
            ip = s.getsockname()[0]
            return ip
    except Exception as e:
        return f"Error: {e}"

def create_client_config(client_data, config_data, quota, days, concurrent_connections):
    """
    This function give imformations which in need to create a user client config file.
    """

    port = config_data['inbounds'][0]['port']
    protocol = config_data['inbounds'][0]['protocol']
    encryption = config_data['inbounds'][0]['settings']['decryption']
    stream_network = config_data['inbounds'][0]['streamSettings']['network']
    header_type = config_data['inbounds'][0]['streamSettings']['tcpSettings']['header']['type']
    security = 'none'
    host = 'google.com'
    ip = get_ip()
    user_name = client_data['email']
    uid = client_data['id']
    readable_quota = convert_size(quota)
    date_range = get_date_range(days)



    config_text = f'{protocol}://{uid}@{ip}:{port}?security={security}&encryption={encryption}&host={host}&headerType={header_type}&type={stream_network}#{user_name}@{readable_quota}@{date_range}@{concurrent_connections}CC'

    user_path = os.path.join('users', user_name)
    if not os.path.exists(user_path):
        os.makedirs(user_path)
    with open(f'./{user_path}/client.config', 'w') as file:
        file.write(config_text)

    
def add_user_to_file(user: str, config_file_path: str, quota: str, days: int,concurrent_connections: int) -> bool:
    """
    Add user to a config file
    Gives a user and path to the conf/inbound.json file and returns True if creation was successfull otherwise returns False.
    """


    with open(config_file_path, 'r') as file:
        file_data = json.load(file)

    clients = file_data["inbounds"][0]["settings"]["clients"]

    for client in clients:
        if user == client['email']:
            return False

    client_dict = create_user(user)
    clients.append(client_dict)
    file_data["inbounds"][0]["settings"]["clients"] = clients

    with open(config_file_path, 'w') as file:
        json.dump(file_data, file, indent=4)


    create_client_config(client_dict, file_data, quota, days, concurrent_connections)
  
    send_log(LOG_PATH, f'added \'{user}\' to \'{config_file_path}\' file.\n')


    # if the user exists before and have statistics for today we should make the today's statistics file for the old one and create a fresh one for today.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_date = current_time.split()[0].split('-')
    this_month_user_stats = os.path.join('users', user, 'Statistics', current_date[0], current_date[1])
    today_user_stats = os.path.join(this_month_user_stats, current_date[2]+'.json')
    if os.path.exists(today_user_stats):
        os.rename(today_user_stats, today_user_stats+'.old')

    return True

def refresh_user_in_file(user: str, config_file_path: str, quota: str, days: int,concurrent_connections: int) -> bool:
    """
    Refresh the user without changing the uuid of it.
    """


    # open the 'conf/inbound.json' with the user
    with open(config_file_path, 'r') as file:
        file_data = json.load(file)
    
    # Extract the clients
    clients = file_data["inbounds"][0]["settings"]["clients"]
    # Extract the uuid of the user
    uuid = None
    for client in clients:
        if user == client['email']:
            uuid = client['id']

    if uuid:
        # delete the user from 'conf/inbound.json'
        deleted = del_user_from_file(user, config_file_path)
    else:
        user_client_config = os.path.join('./users', user, 'client.config')
        if os.path.exists(user_client_config):
            with open(user_client_config, 'r') as file:
                user_client_config_data = file.read()
            uuid = user_client_config_data.split('//')[1].split('@')[0]
        else:
            return False


    # open the 'conf/inbound.json' without the user.
    with open(config_file_path, 'r') as file:
        file_data = json.load(file)

    clients = file_data["inbounds"][0]["settings"]["clients"]
    client_dict = create_user(user, uuid)
    clients.append(client_dict)
    file_data["inbounds"][0]["settings"]["clients"] = clients

    with open(config_file_path, 'w') as file:
        json.dump(file_data, file, indent=4)


    create_client_config(client_dict, file_data, quota, days, concurrent_connections)
  
    send_log(LOG_PATH, f'added \'{user}\' softly to \'{config_file_path}\' file.\n')


    # if the user exists before and have statistics for today we should make the today's statistics file for the old one and create a fresh one for today.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_date = current_time.split()[0].split('-')
    this_month_user_stats = os.path.join('users', user, 'Statistics', current_date[0], current_date[1])
    today_user_stats = os.path.join(this_month_user_stats, current_date[2]+'.json')
    if os.path.exists(today_user_stats):
        os.rename(today_user_stats, today_user_stats+'.old')

    return True


def del_user_from_file(name: str, config_file_path) -> bool:
    """
    Take an str and returns True if successfully deleted the user from conf/inbound.json file and returns False otherwise.
    """
    with open(config_file_path, 'r') as file:
        file_data = json.load(file)

    clients = file_data["inbounds"][0]["settings"]["clients"]
    result_clients = []

    user_exists = False
    for client in clients:
        if name == client['email']:
            user_exists = True
        else:
            result_clients.append(client)

    file_data["inbounds"][0]["settings"]["clients"] = result_clients

    with open(config_file_path, 'w') as file:
        json.dump(file_data, file, indent=4)

    
    if user_exists:
        send_log(LOG_PATH, f'removed \'{name}\' from \'{config_file_path}\' file.\n')
    return user_exists 

def send_log(log_file: str, log_message: str) -> None:
    """ send a log to log_file with timestamp."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = current_time + ' ' + log_message
    file_path = Path(log_file)

    with file_path.open(mode='a') as file:
        file.write(log_message)
