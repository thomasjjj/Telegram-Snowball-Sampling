import os
import csv
import pandas as pd

def merge_csv_files(results_folder, merged_folder, merged_filename):
    merged_file_path = os.path.join(merged_folder, merged_filename)

    # Create 'merged' directory if it doesn't exist
    if not os.path.exists(merged_folder):
        os.makedirs(merged_folder)

    # Check if the merged file already exists and read it
    if os.path.exists(merged_file_path):
        existing_data = pd.read_csv(merged_file_path)
    else:
        existing_data = pd.DataFrame(columns=['Channel ID', 'Channel Name'])

    all_data = []

    # Find and process all CSV files in the 'results' folder
    for file in os.listdir(results_folder):
        if file.endswith('.csv'):
            file_path = os.path.join(results_folder, file)
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                for row in reader:
                    # Extract channel IDs and names from each row
                    for i in range(0, len(row), 2):  # Assuming ID and name are adjacent
                        if row[i]:  # Check if ID is not empty
                            all_data.append((row[i], row[i + 1]))

    # Add new data to existing data and remove duplicates
    new_data = pd.DataFrame(all_data, columns=['Channel ID', 'Channel Name'])
    combined_data = pd.concat([existing_data, new_data]).drop_duplicates().reset_index(drop=True)

    # Write merged data to a new CSV file
    combined_data.to_csv(merged_file_path, index=False, encoding='utf-8')

    print(f"Merged data written to {merged_file_path}")

if __name__ == '__main__':
    # Specify the folders and filename
    results_folder = 'results'
    merged_folder = 'merged'
    merged_filename = 'merged_channels.csv'

    # Call the function
    merge_csv_files(results_folder, merged_folder, merged_filename)
