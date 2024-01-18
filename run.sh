#! /bin/bash

# Run xray in background.
./xray &

# Get the pid of xray command.
xray_pid=$(echo $!)

# check if users.log file is modified and if so restart the xray.
log_path="./users.log"


# Run process_stats_v2.py and police.py in background
python3 process_stats.py &
stats_pid=$(echo $!)
python3 police.py &
police_pid=$(echo $!)
# Set a trap to handle the script's termination signal (usually SIGTERM).
trap 'kill $(echo $stats_pid $police_pid)' EXIT

# Just in case
touch $log_path

previous_size=$(wc -c < "$log_path")
while true; do
	# Get the current size of the file
	current_size=$(wc -c < "$log_path")

	# Check if the size has increased since the last check
	if [ "$current_size" -gt "$previous_size" ]; then
		kill $xray_pid
		./xray run -config config.json -confdir conf &
		xray_pid=$(echo $!)
		previous_size=$current_size
	fi

	# Add a delay before the next check.
	sleep 1
done
