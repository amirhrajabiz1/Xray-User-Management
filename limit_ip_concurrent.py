#!/usr/bin/env python3

"""
This script is for limiting the number of ips who can connect to each UUID.
"""

def is_CC_valid(user_name, max_concurrent_connections, copy_access_file) -> bool:
    """
    This function receive path of the access.log.copy file and and checks the user connetion to see the user has how many connections in the last period.
    if the connections are more that max_concurrent_connections returns False and otherwise return True.
    """
    max_concurrent_connections = int(max_concurrent_connections[:-2])
    with open(copy_access_file) as file:
        all_records = file.readlines()
    email_records = [record for record in all_records if 'email' in record]
    concurrent_connections = set()
    for record in email_records:
        if user_name == record.split()[-1]:
            concurrent_connections.add((record.split()[2].split(':')[0], record.split()[-1]))

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
