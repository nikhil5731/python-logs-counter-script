import re
import csv
import datetime

# Have to change to .log file
log_file_path = "./licenses_logs/Nov23.log"

# To Check whether the date is valid or not
def contains_date(line):
    date_pattern = r"\b(\d{1,2}/\d{1,2}/\d{4})\b"
    match = re.search(date_pattern, line)
    if match:
        return match.group(1)
    else:
        return None

# To filter logs having date
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

# To process all logs and filter logs having some date in it
def process_logs(log_filename):
    log_pattern = r'(\d{1,2}/\d{1,2}/\d{4}) (\d{1,2}:\d{1,2}:\d{1,2}) \((snpslmd)\) (IN|OUT): "(.*?)" (\S+)'

    processed_data = []

    with open(log_filename, "r") as file:
        for line in file:
            match = re.search(log_pattern, line)
            if match:
                date = convert_date_format(match.group(1))
                time = match.group(2)
                action_type = match.group(4)
                device_name = match.group(5)
                user_id = match.group(6).split("@")[0]
                processed_data.append(
                    {
                        "Date": date,
                        "Time": time,
                        "Action Type": action_type,
                        "Device Name": device_name,
                        "User ID": user_id,
                    }
                )

    return processed_data

# to normalize the dates written format
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

# create a csv file
def write_to_csv(data, filename):
    headers = ["Date", "Time", "Action Type", "Device Name", "User ID"]

    device_names = list({row["Device Name"] for row in data})

    # Add device names to headers
    headers.extend(device_names)

    # Write data to CSV file
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        # Initialize the device counts
        device_counts = {device: 0 for device in device_names}

        for row in data:
            # Create output row with initial values
            output_row = {header: row.get(header, "") for header in headers}

            # Update device counts based on the action type
            device_name = row["Device Name"]
            if row["Action Type"] == "IN":
                device_counts[device_name] -= 1
            elif row["Action Type"] == "OUT":
                device_counts[device_name] += 1

            # Add device counts to the output row
            output_row.update(device_counts)

            # Write the updated row to the CSV
            writer.writerow(output_row)


filtered_lines = filter_log_lines(log_file_path)


# Alternatively, write the filtered logs to a new file
with open("filtered.log", "w") as f:
    f.writelines(filtered_lines)


log_filename = "filtered.log"  # Replace with your actual log file name

# Process the log file
processed_data = process_logs(log_filename)

# Write processed data to CSV file
csv_filename = "daily_device_counts.csv"
write_to_csv(processed_data, csv_filename)

print(f"CSV file '{csv_filename}' has been created successfully from '{log_filename}'.")
