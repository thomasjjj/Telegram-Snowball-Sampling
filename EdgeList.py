from utils import *
def create_edge_list(folder_name, file_name, from_channel_id, from_channel_name, from_channel_username, to_channel_id, to_channel_name, to_channel_username):
    # Check if the folder exists, if not, create it
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(folder_name, file_name)

    # Check if file exists, if not, create it with headers
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['From_Channel_ID', 'From_Channel_Name', 'From_Channel_Username', 'To_Channel_ID', 'To_Channel_Name', 'To_Channel_Username'])

    # Append to the file for each message found
    with open(file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([from_channel_id, from_channel_name, from_channel_username, to_channel_id, to_channel_name, to_channel_username])