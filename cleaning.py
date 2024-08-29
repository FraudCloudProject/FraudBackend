import csv

# Path to the input and output CSV files
input_csv_path = 'Dataset_5971.csv'
output_csv_path = 'Dataset_fixed.csv'

# Open the input CSV file for reading and output CSV file for writing
with open(input_csv_path, mode='r', newline='') as input_file, open(output_csv_path, mode='w', newline='') as output_file:
    # Create CSV reader and writer objects
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)

    # Iterate through each row in the input CSV file
    for row in reader:
        # Check if there is at least one word in the row
        if row:
            # Get the first word of the line
            first_word = row[0]
            
            # Check if the first word is "smishing" or "spam" and if the first letter is lowercase
            if first_word.lower() in ('smishing', 'spam') and first_word[0].islower():
                # Convert the first letter to uppercase
                row[0] = first_word.capitalize()
        
        # Write the (possibly modified) row to the output CSV file
        writer.writerow(row)

print(f"Processed CSV file has been saved to {output_csv_path}.")
