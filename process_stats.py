import subprocess
import json
import os
import datetime
from time import sleep


def get_command_output():
    try:
        output = subprocess.check_output(
            [
                './xray',
                'api',
                'statsquery',
                '--pattern',
                'user',
                '-reset',
                '--server=127.0.0.1:8080',
            ]
        )
        return json.loads(output)
    except Exception as e:
        print(f'Error running command: {e}')
        return None


def get_user_day_file_path(user: str) -> str:
    """
    gives us the path of the day file in user statistics directory.
    """
    now = datetime.datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    daypath = os.path.join('users', user, 'Statistics', year, month, day)
    return daypath


def update_traffic_data(user, traffic_type, value):
    file_path = get_user_day_file_path(user) + '.json'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        with open(file_path, 'r+') as file:
            data = json.load(file)
            if traffic_type in data:
                data[traffic_type] = int(value) + data[traffic_type]
            else:
                data[traffic_type] = int(value)
            file.seek(0)
            json.dump(data, file)
            file.truncate()
    else:
        with open(file_path, 'w') as file:
            json.dump({traffic_type: int(value)}, file)


def process_trafic_data(data):
    for item in data.get('stat', []):
        parts = item['name'].split('>>>')
        if len(parts) == 4 and parts[0] == 'user':
            user, traffic_type = parts[1], parts[-1]
            value = item['value']
            # if not os.path.exists(user):
            #  os.makedirs(user + '1')
            update_traffic_data(user, traffic_type, value)


def main():
    while True:
        data = get_command_output()
        if data:
            process_trafic_data(data)
        sleep(5)  # Run the command every second


if __name__ == '__main__':
    main()
