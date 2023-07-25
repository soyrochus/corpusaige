import csv
import os

# Define the path to the CSV file
csv_file_path = 'ResumeDataSet.csv'

# Initialize the sequential ID
seq_id = 1

# Open the CSV file
with open(csv_file_path, 'r',  encoding='utf-8', errors='ignore') as csvfile:
    # Create a CSV reader
    csvreader = csv.reader(csvfile)

    # Ignore the first row of column names
    next(csvreader)

    # Process each row in the CSV file
    for row in csvreader:
        # Extract the category and resume from the row
        category, resume = row

        # Define the name of the text file
        text_file_name = 'CV-{}.txt'.format(seq_id)

        # Open the text file
        with open(text_file_name, 'w', encoding='utf-8', errors='ignore') as textfile:
            textfile.write('_________ begin resume _________\n')
            # Write the ID, category, and resume to the text file
            textfile.write('id: {}\n'.format(seq_id))
            textfile.write('Category {}\n'.format(category))
            textfile.write('Resume:\n\n{}\n'.format(resume))
            textfile.write('_________ end resume _________\n')

        # Increment the sequential ID
        seq_id += 1
