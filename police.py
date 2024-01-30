from typing import Tuple
import os
from datetime import datetime, timedelta
import json
import time
from typing import NamedTuple

from process_users import convert_to_bytes, del_user_from_file, send_log
from limit_ip_concurrent import files_management, is_CC_valid


CONFIG_PATH = 'conf/inbound.json'
ACCESS_LOG_PATH = 'access.log'
REASON_REMOVE_LOG_PATH = 'reasonremove.log'


def extract_date_quota_CC_from_client_file(
    user_name: str,
) -> Tuple[str, str, str]:
    """
    give the name of the user and return the date and quota and concurrent connections of the user from user.json of that user.
    """
    user_path = os.path.join('users', user_name)
    config_path = os.path.join(user_path, 'user.json')

    with open(config_path, 'r') as file:
        client_config_json = json.load(file)

    date = client_config_json['date']
    quota = client_config_json['quota']
    CC = client_config_json['concurrent_connections']

    return date, quota, CC


def is_user_valid(user_name: str) -> str:
    """
    Give the name of the user and return the state of the user (valid, time_out, quota_out or concurrent connection violation).
    """
    user_stats_path = os.path.join('users', user_name, 'Statistics')
    if os.path.exists(user_stats_path):
        (
            user_date,
            user_quota,
            user_CC,
        ) = extract_date_quota_CC_from_client_file(user_name)

        time_valid = is_time_valid(user_stats_path, user_date)

        quota_valid = is_quota_valid(user_stats_path, user_quota, user_date)

        CC_valid = is_CC_valid(user_name, user_CC, f'{ACCESS_LOG_PATH}.copy')

        if not quota_valid:
            return 'quota_out'
        elif not time_valid:
            return 'time_out'
        elif not CC_valid:
            return 'CC_violation'
        return 'valid'
    else:
        # If there wasn't any Statistics for the user the user is new and is valid.
        return 'valid'


def is_time_valid(user_stats_path: str, user_date: str) -> bool:
    """
    Return True if user still has time and return False otherwise.
    """
    used_max_year = max(os.listdir(user_stats_path))
    months_path = os.path.join(user_stats_path, used_max_year)
    used_max_month = max(os.listdir(months_path))
    days_path = os.path.join(months_path, used_max_month)
    used_max_day = max([day.split('.')[0] for day in os.listdir(days_path)])

    limit_end_date = user_date.split('-')[1]
    limit_end_year = limit_end_date[:4]
    limit_end_month = limit_end_date[4:6]
    limit_end_day = limit_end_date[6:]

    if used_max_year > limit_end_year:
        return False
    elif used_max_year == limit_end_year:
        if used_max_month > limit_end_month:
            return False
        elif used_max_month == limit_end_month:
            if used_max_day > limit_end_day:
                return False
            else:
                return True
        else:
            return True
    else:
        return True


def is_quota_valid(
    user_stats_path: str, user_quota: str, user_date: str
) -> bool:
    """
    Return True if user still has quota and return False otherwise.
    """
    used_bandwidth = 0
    dates_user_can_use = create_days_set_between_two_dates(user_date)
    for root, dirs, files in os.walk(user_stats_path):
        for file in files:
            if file.endswith('.json'):
                # Get the relative path of the file
                rel_path = os.path.relpath(
                    os.path.join(root, file), user_stats_path
                )
                # Replace the path seprators with dashes
                file_name = rel_path.replace(os.sep, '-')
                plain_file_name = file_name.replace('.json', '')
                if plain_file_name in dates_user_can_use:
                    full_path_of_file = os.path.join(user_stats_path, rel_path)
                    used_bandwidth += read_stat_file(full_path_of_file)

    user_quota_bytes = convert_to_bytes(user_quota)
    if user_quota_bytes > used_bandwidth:
        return True
    return False


def read_stat_file(full_path_of_file: str) -> int:
    """
    get the address of a stat file like 'users/sushi/Statistics/2023/12/12.json' and return the
    sum of uplink and downlink for that stat.
    """
    with open(full_path_of_file, 'r') as file:
        data = json.load(file)
    uplink = data['uplink']
    downlink = data['downlink']
    sumlink = uplink + downlink
    return sumlink


def create_days_set_between_two_dates(dates: str) -> set:
    """
    get an str like this '20231212-20240111' and return a set like this:
    {'2023-12-12', '2023-12-13', '2023-12-14', ..., '2024-1-11'}
    """

    start_date = datetime.strptime(dates.split('-')[0], '%Y%m%d')
    end_date = datetime.strptime(dates.split('-')[1], '%Y%m%d')

    result_dates = set()

    for i in range((end_date - start_date).days + 1):
        result_dates.add((start_date + timedelta(days=i)).strftime('%Y-%m-%d'))

    return result_dates


def check_users_validity(config_file: str) -> None:
    """
    This function iterate through users in conf/inbound.json file and decide whether users are eligible to have access to the service.
    """
    while True:
        with open(config_file, 'r') as file:
            file_data = json.load(file)

        clients = file_data['inbounds'][0]['settings']['clients']
        usernames = [client['email'] for client in clients]

        for username in usernames:
            user_status = is_user_valid(username)
            if user_status != 'valid':
                user_deleted_successfully = del_user_from_file(
                    username, config_file
                )
                if user_deleted_successfully:
                    send_log(
                        REASON_REMOVE_LOG_PATH,
                        f"user '{username}' removed because of {user_status}.\n",
                    )
            else:
                # print('user', f'\'{username}\'', 'stays.')
                pass

        files_management(ACCESS_LOG_PATH)
        time.sleep(10)


def main() -> None:
    check_users_validity(CONFIG_PATH)


if __name__ == '__main__':
    main()
