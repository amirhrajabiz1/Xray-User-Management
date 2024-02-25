#!/usr/bin/env python3

import os

"""
This script is for limiting the number of ips who can connect to each UUID.
"""


def get_email_records_from_access_copy(copy_access_file: str) -> list:
    """
    return the records from copy_access_file which have 'email' in them.
    """
    if not os.path.exists(
        copy_access_file
    ):   # create the copy_access_file if it doesn't exist.
        with open(copy_access_file, 'w') as fp:
            pass
    with open(copy_access_file) as file:
        all_records = file.readlines()
    email_records = [record for record in all_records if 'email' in record]
    return email_records


def is_CC_valid(
    user_name, max_concurrent_connections, copy_access_file
) -> bool:
    """
    This function receive path of the access.log.copy file and and checks the user connetion to see the user has how many connections in the last period.
    if the connections are more that max_concurrent_connections returns False and otherwise return True.
    """
    max_concurrent_connections = int(max_concurrent_connections)
    email_records = get_email_records_from_access_copy(copy_access_file)
    concurrent_connections = set()
    for record in email_records:
        user_in_record = record.split()[-1]
        if user_name == user_in_record:
            ip_port = record.split()[2]
            # check the ip is version 4 or 6
            if '[' in ip_port:
                temp = ip_port.split(':')
                ip = ':'.join(temp[:-1])    # IPv6
            else:
                ip = ip_port.split(':')[0]  # IPv4

            concurrent_connections.add(ip)

    if len(concurrent_connections) > max_concurrent_connections:
        return False
    return True


def files_management(original_access_path: str):
    """
    moves all content of original_access_path to the copy_access_path file.
    """
    copy_access_path = original_access_path + '.copy'
    try:
        with open(original_access_path, 'r') as file:
            original_text = file.read()
    except FileNotFoundError:
        print(f'{original_access_path} not found')
    with open(original_access_path, 'w') as file:
        pass

    with open(copy_access_path, 'w') as file:
        file.write(original_text)
