import os
import pandas as pd
import pickle

# Define the folder path
folder_path = 'c:\\Users\\ousep\\OneDrive\\Documents\\phase2\\LabLab Hackathon\\ShopAssist\\ShopAssist\\picklefiles\\'

def read_pickle_files(folder_path, keyword):
    # Get a list of all pickle files in the folder
    pickle_files = [file for file in os.listdir(folder_path) if (file.endswith('.pkl') and keyword in file)]
    print('pickle files are: ',pickle_files)
    # Read each pickle file into a dataframe
    dataframes = []
    for file in pickle_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'rb') as f:
            dataframe = pickle.load(f)
            dataframes.append(dataframe)
    combined_dataframe = pd.concat(dataframes)
    return combined_dataframe

# Call the function for all-posts
all_posts_dataframe = read_pickle_files(folder_path, 'all-posts-0527')

# Call the function for all-profiles
all_profiles_dataframe = read_pickle_files(folder_path, 'all-profiles0527')

# Call the function for all-errors
all_errors_dataframe = read_pickle_files(folder_path, 'all-errors0527')

# Now you have a list of dataframes containing the data from the pickle files
# You can perform further operations on these dataframes as needed

# Check for duplicate records in post_id column
duplicate_records = all_posts_dataframe.duplicated(subset=['post_id'])

# Print the duplicate records
print('Duplicate records in post_id column:')
print(all_posts_dataframe[duplicate_records])

# Create a table of count of post_id by creatorid
post_count_by_creatorid = all_posts_dataframe.groupby('creatorid')['post_id'].count().reset_index()
print(post_count_by_creatorid)

# Drop duplicate records based on creatorid and keep the latest records using date refreshed column
all_profiles_dataframe = all_profiles_dataframe.sort_values('date_refreshed').drop_duplicates('creatorid', keep='last').reset_index(drop=True)

# Save the dataframes as pickle files
all_profiles_dataframe.to_pickle(folder_path + 'all-profiles.pkl')
all_posts_dataframe.to_pickle(folder_path + 'all-posts.pkl')
all_errors_dataframe.to_pickle(folder_path + 'all-errors.pkl')