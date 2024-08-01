import pandas as pd
import numpy as np
import re
import os

print("Directory to Loop Through: ")
basePath = input("> ")
print("Catalog to remove from DDL: ")
namespace = input("> ")

folderName = os.path.basename(basePath)

def fix_schema_errors(basePath: str, namespace: str):
    print('\n')
    print(f'Applying schema mismatch fixes to {folderName} table.')
    loc_pattern = "LOCATION '.*'"
    tbl_prop_pattern = "TBLPROPERTIES.*"
    table_pattern = "TABLE"
    # ddl_pattern = "\([^()]*\)"
    

    print(f'Working on: {folderName} ...')
    directory = os.fsencode(basePath)

    for file in os.listdir(directory):
        fileName = os.fsdecode(file)
        print(fileName)
        try:
            with open(fileName, "r") as f:
                print(f"Opened file {fileName}")
                ddl = f.read()
                print(ddl)
                x = re.search(table_pattern, ddl)
                y = re.search(table_pattern, ddl)
                print(f"Removing {namespace} from Create Statement")
                # ddl = re.sub(f'{namespace}.', '', ddl)
                # ddl = re.sub(r'\([^()]*\)', '', ddl)
                # ddl = re.sub(tbl_pattern, '', ddl)

                if x and y:
                    print(f"Removing {namespace} from Create Statement")
                    ddl = re.sub(f'{namespace}.', '', ddl)
                    print('Removing schema definition from ddl')
                    ddl = re.sub(r'\([^()]*\)', '', ddl)
                    if re.search(tbl_prop_pattern, ddl):
                        ddl = re.sub(tbl_prop_pattern, '', ddl)
                else:
                    print(f'No Location in DDL in {fileName}, skipping...')
            with open(fileName, 'w') as file:
                file.write(ddl)

        except AttributeError:
            print('Failure')
            
fix_schema_errors(basePath, namespace)