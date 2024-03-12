import os
import json
import re

# Importing functions from external modules
from limit_ip_concurrent import get_email_records_from_access_copy
from process_stats import get_user_day_file_path


def analyze_email_records(copy_access_file: str) -> dict:
    """
    Analyze email records from the provided access copy file and
    return a dictionary containing user names as keys and their
    associated domains with the number of requests as values.
    """
    output_dict = dict()

    # Retrieve email records from the access copy file
    email_records = get_email_records_from_access_copy(copy_access_file)

    # Split each email record into parts
    splited_email_records = [
        email_record.split() for email_record in email_records
    ]

    # Extract useful parts from each split email record
    useful_parts_splited_email_records = [
        splited_email_record[splited_email_record.index('accepted')+1:]
        for splited_email_record in splited_email_records
    ]

    # Iterate through each useful part of the split email records
    for record in useful_parts_splited_email_records:
        # Extract username
        username = ' '.join(record[record.index('email:')+1:])
        # Extract request info
        request_info = ' '.join(record[:record.index('email:')])
        # Update the output dictionary
        output_dict[username] = output_dict.get(username, {})
        output_dict[username][request_info] = (
            output_dict[username].get(request_info, 0) + 1
        )

    return output_dict


def user_domains_statistics_logs(user_domains_statistics_path: str) -> dict:
    """
    Retrieve the content of the user's domain log statistics from the provided path
    and return it as a dictionary. If the file doesn't exist, return an empty dictionary.
    """
    # Ensure the directory structure exists
    os.makedirs(os.path.dirname(user_domains_statistics_path), exist_ok=True)

    # Create the file if it doesn't exist
    if not os.path.exists(user_domains_statistics_path):
        with open(user_domains_statistics_path, 'w') as fp:
            pass

    # Attempt to read and decode the JSON file
    with open(user_domains_statistics_path) as file:
        try:
            output_dict = json.load(file)
        except json.decoder.JSONDecodeError:
            output_dict = {}

    return output_dict


def merge_two_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Merge two dictionaries, summing the values of common keys.
    """
    merged_dict = dict()

    # Iterate through the keys of both dictionaries
    for key in dict1.keys() | dict2.keys():
        # Add the values for common keys, or use 0 if not present in one dictionary
        merged_dict[key] = dict1.get(key, 0) + dict2.get(key, 0)

    return merged_dict


def store_domains(domains_dict, user_stored_domains_path: str) -> None:
    """
    Store the provided domains dictionary as a JSON file at the specified path.
    """
    with open(user_stored_domains_path, 'w') as file:
        json.dump(domains_dict, file)


def domains_logging(access_log_path: str) -> None:
    """
    Read the content of the access log file, analyze it to retrieve user domains,
    and store the requested domains for each user in their specific statistics path.
    If the user's statistics file already exists, merge the new data with the existing data.
    """
    # Generate the path for the access copy file
    access_copy_path = access_log_path + '.copy'

    # Analyze the email records from the access copy file
    user_access_domains = analyze_email_records(access_copy_path)

    # Iterate through each user and their associated domains
    for user, domains in user_access_domains.items():
        # Generate the path for storing the user's domain statistics
        user_stored_domains_path = (
            get_user_day_file_path(user) + '_domains.json'
        )

        # Retrieve the existing domain statistics for the user
        user_stored_domains = user_domains_statistics_logs(
            user_stored_domains_path
        )

        # Merge the new domains with the existing domain statistics
        merged_domains = merge_two_dicts(domains, user_stored_domains)

        # Store the merged domain statistics
        store_domains(merged_domains, user_stored_domains_path)
