'''
This script creates an asset mapping Excel spreadsheet using the csvs created by convert_all_logs.py
Each csv gets its own sheet and adds a tag column for the customer to tag assets
The resulting .xlsx file can be imported into a Google Sheet
'''

import os, csv, openpyxl
csv.field_size_limit(10000000)  # Allows up to 10 million characters in a field

def csv_to_excel(input_folder):
    
    # Instantiate a new Excel workbook
    workbook = openpyxl.Workbook()

    # Loop through csv's and read each one line-by-line using csv.reader
    for csv_file in os.listdir(input_folder):
        csv_data = []

        full_path = input_folder + '/' + csv_file

        with open(full_path) as file_obj:
            reader = csv.reader(file_obj)
            for row in reader:
                csv_data.append(row)
        
        # Use the name of the csv file as the sheet name
        sheet_name = os.path.splitext(csv_file)[0]

        # Create new sheet
        workbook.create_sheet(title=sheet_name)
        sheet = workbook[sheet_name]
        
        # Insert csv data into sheet
        for row in csv_data:
            sheet.append(row)

        # Insert a tag column before column at index 2
        sheet.insert_cols(2)
        sheet['B1'] = 'tag'

        # Freeze the first row and first two columns
        sheet.freeze_panes = sheet['C2']

        # Resizing columns to fit cell contents, has a max value in case columns are very wide
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter # Get the column name
            for cell in col:
                try: # Necessary to avoid error on empty cells
                    if len(str(cell.value)) > 0:
                        max_length = len(str(cell.value))
                except:
                    pass

            # Copied this formula from an example, seems to do a good job
            adjusted_width = round((max_length + 2) * 1.2, 0)
            
            # Keeps column widths from getting too large, 75 is arbitrary
            if adjusted_width > 75:
                adjusted_width = 75

            sheet.column_dimensions[column].width = adjusted_width

    # Remove the default sheet
    default_sheet = workbook['Sheet']
    workbook.remove(default_sheet)

    # Save the Excel file
    workbook.save("asset_mapping.xlsx")

def main():
    csv_to_excel(os.getcwd() + '/csv')

if __name__ == "__main__":
    main()
