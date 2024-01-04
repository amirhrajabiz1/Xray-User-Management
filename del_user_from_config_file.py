import sys
import argparse

from process_users import del_user_from_file

def process_args():
    parser = argparse.ArgumentParser(
            description='Delete a user to conig.json')
    parser.add_argument(
            '-u', '--user', type=str, help="user name")
    parser.add_argument(
            '-c', '--config_file', type=str, help="config.json path")

    args = parser.parse_args()
    return args.user, args.config_file

if __name__ == '__main__':
    name, file_path = process_args()

    deleted = del_user_from_file(name, file_path)

    if deleted:
        print(f"Successfully deleted '{name}' from '{file_path}'.")
    else:
        print(f"Failed to delete '{name}' from '{file_path}'.")
