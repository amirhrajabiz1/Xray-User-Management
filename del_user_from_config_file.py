import sys
import argparse
import shutil
import os

from process_users import del_user_from_file, send_log


DEFAULT_CONFIG_PATH = 'conf/inbound.json'
REASON_REMOVE_LOG_PATH = 'reasonremove.log'


def remove_directory(path: str) -> None:
    """
    Remove the directory in path.
    """
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' successfully deleted.")
    except OSError as e:
        print(f'Error {e}')


def process_args():
    parser = argparse.ArgumentParser(
        description=f"Delete a user from '{DEFAULT_CONFIG_PATH}'"
    )
    parser.add_argument(
        '-u', '--user', required=True, type=str, help='user name'
    )
    parser.add_argument(
        '-c',
        '--config_file',
        default=DEFAULT_CONFIG_PATH,
        type=str,
        help=f'config path (default={DEFAULT_CONFIG_PATH})',
    )
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Use this if you want delete the user statistics and information completely.',
    )

    args = parser.parse_args()
    return args.user, args.config_file, args.force


if __name__ == '__main__':
    name, file_path, force = process_args()

    deleted = del_user_from_file(name, file_path)

    if deleted:
        print(f"Successfully deleted '{name}' from '{file_path}'.")
        send_log(REASON_REMOVE_LOG_PATH, f"user '{name}' removed manually.\n")
        remove_directory(os.path.join('users', name))

    else:
        print(f"Failed to delete '{name}' from '{file_path}'.")
