import pandas as pd
import json
import os
import math
import sys

def change_filename(current_relative_path: str, new_relative_path: str) -> None:
    current_directory = os.getcwd()
    current_full_path = os.path.join(current_directory, current_relative_path)
    new_full_path = os.path.join(current_directory, new_relative_path)
    os.rename(current_full_path, new_full_path)

def write_jsonl(file_relative_path: str, data: list) -> None:
    current_directory = os.getcwd()
    file_full_path = os.path.join(current_directory, file_relative_path)

    with open(file_full_path, "w") as f:
        for item in data:
            json.dump(item, f)
            f.write("\n")

# Pull spreadsheet from filesystem and save in dataframe
# TODO: Read spreadsheet directly from Teams/OneDrive (permission issues)
file_path = "../raw_data/test_yes_no.xlsx"
df = pd.read_excel(file_path)

pd.set_option("display.max_columns", None)
print(df.head())

# Shuffle dataframe
shuffled_data = df.sample(frac=1).reset_index(drop=True)

pd.set_option("display.max_columns", None)
print(shuffled_data.head())

# Create an empty list to append to later
json_data_list = []

# Iterate through all items of dataframe and create the properly formatted Python dict
for index, row in shuffled_data.iterrows():
    yes_value = 1 if row["Label"].lower() == "yes" else 0 
    no_value = 1 if row["Label"].lower() == "no" else 0
    d = {
        "text": f"{row['Question']} {row['Response']}",
        "cats": {"YES": yes_value,
                 "NO": no_value
                 }
    }

    # Append the python dict to the list
    json_data_list.append(d)

# print(json_data_list)
    
# Rename existing training file to given version
relative_path_to_current_filename = "../assets/yes_no_training.jsonl"

ARCHIVE_VERSION = "0.1.3"
relative_path_to_new_filename = f"../assets/yes_no_training_{ARCHIVE_VERSION}.jsonl"

if not os.path.exists(relative_path_to_current_filename):
    print("yes_no_training.jsonl doesn't exist! Can't change filename, exiting script...")
    sys.exit(1)

if os.path.exists(relative_path_to_new_filename):
    print(f"yes_no_training_{ARCHIVE_VERSION}.jsonl already exists! Don't want to overwrite anything, exiting script...")
    sys.exit(1)
    
change_filename(relative_path_to_current_filename, relative_path_to_new_filename)
    

# Rename existing eval file to given version
relative_path_to_current_filename = "../assets/yes_no_eval.jsonl"

relative_path_to_new_filename = f"../assets/yes_no_eval_{ARCHIVE_VERSION}.jsonl"

if not os.path.exists(relative_path_to_current_filename):
    print("yes_no_eval.jsonl doesn't exist! Can't change filename, exiting script...")
    sys.exit(1)

if os.path.exists(relative_path_to_new_filename):
    print(f"yes_no_eval_{ARCHIVE_VERSION}.jsonl already exists! Don't want to overwrite anything, exiting script...")
    sys.exit(1)

change_filename(relative_path_to_current_filename, relative_path_to_new_filename)

# Calculate 75% of list to be placed in training set and write to new file
training_cutoff = math.floor(0.75*len(json_data_list))
training_set = json_data_list[0:training_cutoff]

training_relative_filename = "../assets/yes_no_training.jsonl"
if os.path.exists(training_relative_filename):
    print("yes_no_training.jsonl already exists! Something went wrong, exiting script")
    sys.exit(1)
else:
    write_jsonl(training_relative_filename, training_set)


# Calculate 25% of list to be place in eval set and write to new file
eval_set = json_data_list[training_cutoff:]

eval_relative_filename = "../assets/yes_no_eval.jsonl"
if os.path.exists(eval_relative_filename):
    print("yes_no_eval.jsonl already exists! Something went wrong, exiting script")
    sys.exit(1)
else:
    write_jsonl(eval_relative_filename, eval_set)



