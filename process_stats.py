import json
import datetime
import time
import subprocess
import os


# Function to execute the command and return the JSON output
def execute_command():
    command = "./xray api statsquery --pattern 'user'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

prev_data_stat_value = dict()
def process_datas(file_data, data, flag):
    if file_data:
        result = list()
        file_data = file_data["stat"]
        data = data["stat"]
        added_data_stats = list()
        added_file_data_stats = list()
        for data_stat_index, data_stat in enumerate(data):
            for file_data_stat_index, file_data_stat in enumerate(file_data):
                if file_data_stat["name"] == data_stat["name"]:
                    if int(file_data_stat["value"]) > int(data_stat["value"]):
                        if (int(file_data_stat["value"]) + (int(data_stat["value"]) - int(prev_data_stat_value.get(data_stat['name'], 0))) < int(file_data_stat["value"])):
                            value = file_data_stat["value"]
                        else:
                            value = str(int(file_data_stat["value"]) + (int(data_stat["value"]) - int(prev_data_stat_value.get(data_stat['name'], 0))))
                    else:
                        value = data_stat["value"]
                    result_dict = {"name": file_data_stat["name"], "value": value}
                    result.append(result_dict)
                    added_data_stats.append(data_stat)
                    added_file_data_stats.append(file_data_stat)
                    break
            if flag:
                prev_data_stat_value[data_stat['name']] = data_stat['value']
        result.extend([x for x in data if x not in added_data_stats])
        result.extend([x for x in file_data if x not in added_file_data_stats])
    else:
        result = data["stat"]

    final_result = {"stat": result}
    return final_result

# Function to write data to a text file for the specified filename
def write_to_file(filename, data, flag=False):

    try:
        with open(filename, 'r') as file:
            file_data = json.load(file)
    except FileNotFoundError:
        print(f"The file '{filename}' does not exists.")
        file_data = None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        file_data=None

    processed_data = process_datas(file_data, data, flag)

    try:
        with open(filename, 'w') as file:
            json.dump(processed_data, file, indent=4)
    except Exception as e:
        print(f"An error occurred: {e}")
        


while True:
    # Get the current timestamp
    now = datetime.datetime.now()

    # Format the timestamp for year, month, and day
    year = now.strftime("%Y")
    month = now.strftime("%Y-%m")
    day = now.strftime("%Y-%m-%d")

    # Execute the command and get the JSON output
    json_output = execute_command()

    try:
        # Parse the JSON output
        data = json.loads(json_output)

        # Write data to files for today, month, and year
        write_to_file(f"{day}.json", data)
        write_to_file(f"{month}.json", data)
        write_to_file(f"{year}.json", data, True) # True is for flag argument and store the previous value of stats in a dict for calculations.

    except json.JSONDecodeError:
        prev_data_stat_value = dict()
        print("Error parsing JSON output")

    # Wait for 5 minutes before the nex execution
    time.sleep(1)
