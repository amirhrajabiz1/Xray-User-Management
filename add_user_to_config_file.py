import sys
import argparse
import os

from process_users import add_user_to_file, convert_to_bytes, del_user_from_file, refresh_user_in_file

def process_args():
    parser = argparse.ArgumentParser(
            description='Add a user to conig.json and user directory')
    parser.add_argument(
            '-u', '--user', type=str, help="user name")
    parser.add_argument(
            '-c', '--config_file', type=str, help="config.json path")
    parser.add_argument(
            '-l', '--limit',metavar="BANDWIDTH", type=str, help="limit of bandwidth in (B, MB, GB, ...)")
    parser.add_argument(
            '-d', '--day', metavar="days", type=int, help="number of days the user can use the service")
    parser.add_argument(
            '-s', '--simultaneous', metavar="CONNECTIONS", type=int, help="number of simultaneous connection for the user")
    parser.add_argument(
            '-f', '--force', choices=['soft', 'hard'], help="Delete the user. 'soft' will just refresh the statistics. 'hard' will delete the user completely and creates it again.")

    
    args = parser.parse_args()
    if args.force:
        force_arg = args.force
    else:
        force_arg = None
    return args.user, args.config_file, args.limit, args.day, args.simultaneous, force_arg


if __name__ == "__main__":
    name, file_path, quota, days, concurrent_connections, force = process_args()

    # check if the client file exists for this user and if the file exists the added will be False
    user_client_path = os.path.join('./users', name, 'client.config')
    if os.path.exists(user_client_path):
        added = False
    else:
        added = add_user_to_file(name, file_path, convert_to_bytes(quota), days,concurrent_connections)

    if added:
        print(f"Successfully added '{name}'.")
    else:
        if not force:
            print(f"'{name}'s information already exists. use -f {{soft,hard}} to replace the user.")
        elif force == 'hard':
            del_user_from_file(name, file_path)
            added = add_user_to_file(name, file_path, convert_to_bytes(quota), days,concurrent_connections)
            if added:
                print(f"Successfully deleted and created '{name}' again.")
            else:

                print(f"Failed to hardly create user '{name}'")
        elif force == 'soft':
            refreshed = refresh_user_in_file(name, file_path, convert_to_bytes(quota), days,concurrent_connections)
            if refreshed:
                print(f"Successfully deleted and created '{name}' while keeping the old uuid.")
            else:
                print(f"Failed to softly create user '{name}'.")

