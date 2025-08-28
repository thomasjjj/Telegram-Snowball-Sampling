import os
import pandas as pd
import csv


def merge_csv_files(results_folder: str, merged_folder: str, merged_filename: str) -> None:
    """Merge CSV files from the results directory into a deduplicated CSV.

    Args:
        results_folder: Directory containing individual result CSV files.
        merged_folder: Directory where the merged CSV will be stored.
        merged_filename: Name of the output merged CSV file.
    """

    print('Merging and de-duplicating CSVs...')
    merged_file_path = os.path.join(merged_folder, merged_filename)

    # Create 'merged' directory if it doesn't exist
    if not os.path.exists(merged_folder):
        os.makedirs(merged_folder)

    # Read existing data from the merged file or create a new DataFrame
    if os.path.exists(merged_file_path):
        existing_data = pd.read_csv(merged_file_path)
    else:
        existing_data = pd.DataFrame(columns=['Channel ID', 'Channel Name', 'Channel Username'])

    # Convert existing data to a set of tuples for easy lookup
    existing_records = set(tuple(row) for _, row in existing_data.iterrows())

    # Process all CSV files in the 'results' folder and add new data
    all_data = []
    for file in os.listdir(results_folder):
        if file.endswith('.csv'):
            file_path = os.path.join(results_folder, file)
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                for row in reader:
                    if row and tuple(row) not in existing_records:  # Check if the row is not empty and not already in existing data
                        all_data.append(row)
                        existing_records.add(tuple(row))  # Add to existing records to prevent future duplicates

    # Add new data to existing data
    new_data = pd.DataFrame(all_data, columns=['Channel ID', 'Channel Name', 'Channel Username'])
    combined_data = pd.concat([existing_data, new_data])

    # Remove duplicates and reset index
    combined_data.drop_duplicates(inplace=True)
    combined_data.reset_index(drop=True, inplace=True)

    # Write merged data to a new CSV file
    combined_data.to_csv(merged_file_path, index=False, encoding='utf-8')

    print(f"Merged data written to {merged_file_path}")




if __name__ == '__main__':
    # Specify the folders and filename
    results_folder, merged_folder, merged_filename = 'results', 'merged', 'merged_channels.csv'
    merge_csv_files(results_folder, merged_folder, merged_filename)  # Call the function
