import re
import csv
from collections import defaultdict
import datetime


def contains_date(line):
    date_pattern = r"\b(\d{1,2}/\d{1,2}/\d{4})\b"
    match = re.search(date_pattern, line)
    if match:
        return match.group(1)
    else:
        return None


def filter_log_lines(log_file):
    filtered_lines = []
    latest_date = ""

    with open(log_file, "r") as f:
        for line in f:
            if contains_date(line):
                latest_date = contains_date(line)
            if "IN:" in line or "OUT:" in line:
                filtered_lines.append(latest_date + " " + line)

    return filtered_lines


def convert_date_format(date_str):
    try:
        # Attempt to parse the date using different format codes
        date_formats = ["%m/%d/%Y", "%m-%d-%Y", "%m/%d/%y", "%m-%d-%y"]
        for format in date_formats:
            try:
                date_obj = datetime.datetime.strptime(date_str, format)
                return date_obj.strftime("%m/%d/%Y")  # Format as mm/dd/yyyy
            except ValueError:
                continue  # Try the next format if parsing fails
        # If no format matches, return the original date string
        return date_str
    except Exception as e:
        print(f"Error converting date '{date_str}': {e}")
        return date_str


def process_log_file(log_filename):
    # Define the regex pattern to extract relevant information from each line
    log_pattern = r'(\d{1,2}/\d{1,2}/\d{4}) (\d{1,2}:\d{1,2}:\d{1,2}) \((snpslmd)\) (IN|OUT): "(.*?)" (\S+)'

    # Initialize a dictionary to store processed data
    daily_device_data = defaultdict(lambda: defaultdict(int))

    # Read from the log file
    with open(log_filename, "r") as file:
        for line in file:
            match = re.search(log_pattern, line)
            if match:
                date = convert_date_format(match.group(1))
                action_type = match.group(4)
                device_name = match.group(5)

                if action_type == "IN":
                    daily_device_data[date][device_name] += 1
                elif action_type == "OUT":
                    daily_device_data[date][device_name] -= 1

    # Initialize a list to store final processed data
    processed_data = []

    # Aggregate count for each device on each date
    for date, devices in daily_device_data.items():
        row = {"Date": date}
        for device_name in sorted(devices.keys()):
            row[device_name] = devices[device_name]
        processed_data.append(row)

    return processed_data


def write_to_csv(data, filename):
    # Extract headers from the first row of data
    headers = ["Date"] + sorted(
        set(device for row in data for device in row.keys() if device != "Date")
    )

    # Write data to CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            output_row = {header: row.get(header, "No logs!") for header in headers}
            writer.writerow(output_row)


log_file_path = "./licenses_logs/" + input("Enter filename of logs: ")  # Replace with your actual log file path
filtered_lines = filter_log_lines(log_file_path)


# Alternatively, write the filtered lines to a new file
with open("filtered.log", "w") as f:
    f.writelines(filtered_lines)


# Example usage:
log_filename = "filtered.log"  # Replace with your actual log file name

# Process the log file
processed_data = process_log_file(log_filename)

# write processed data to json file
json_filename = "daily_device_counts.json"
with open(json_filename, "w") as file:
    import json

    json.dump(processed_data, file, indent=4)

# Write processed data to CSV file
csv_filename = "daily_device_counts.csv"
write_to_csv(processed_data, csv_filename)

print(f"CSV file '{csv_filename}' has been created successfully from '{log_filename}'.")
