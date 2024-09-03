import os
import argparse
import json

class MetastoreUpdater:
    
    def __init__(self, metastore_logs, root_bucket, mount_point, database_details_log):
        self.metastore_logs = metastore_logs
        self.root_bucket = root_bucket
        self.database_details_log = database_details_log
        if mount_point:
            self.mount_point = mount_point
        else:
            self.mount_point = False
        self.errors = {}
        self.updated_ddls = {}
        
    def duplicate_metastore_as_backup(self):
        # Get the path up one level from self.metastore_logs
        backup_dir = os.path.join(os.path.dirname(self.metastore_logs), 'metastore_backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        for i in os.listdir(self.metastore_logs):
            if i not in ['backup', '.DS_Store', '.ipynb_checkpoints']:
                os.system(f"cp -r {os.path.join(self.metastore_logs, i)} {backup_dir}")
                
    def get_database_details_log(self):
        # get the database details log
        with open(self.database_details_log, 'r') as f:
            db_details = f.read()
        
        # split the log by new line
        db_details = db_details.split('\n')
        
        # get the database details
        database_details = {}
        for db in db_details:
            try:
                db = json.loads(db)
                db_name = db['Namespace Name']
                db_location = db['Location']
                database_details[db_name] = db_location
            except json.decoder.JSONDecodeError:
                print("Error decoding JSON for database:", db)
                continue
            
        return database_details
            
        
    def update_metastore(self):
        db_list = [i for i in os.listdir(self.metastore_logs) if i not in ['.DS_Store', '.ipynb_checkpoints']]

        for db in db_list:
            db_path = os.path.join(self.metastore_logs, db)

            table_list = [i for i in os.listdir(db_path) if i not in ['.DS_Store', '.ipynb_checkpoints']]

            for table in table_list:
                table_path = os.path.join(db_path, table)

                with open(table_path, 'r') as f:
                    ddl = f.read()

                if "location '" in ddl.lower():
                    self.errors[db + table] = "location found in ddl" + ddl
                    continue

                if "create view" in ddl.lower():
                    self.errors[db + table] = "create view found in ddl" + ddl
                    continue
                
                if db != 'default':
                    db_details_dict = self.get_database_details_log()
                    if db in db_details_dict:
                        location = db_details_dict[db] + "/" + table
                    else:
                        print(f"ERROR: Database {db} not found in database details log")
                        continue

                new_ddl = ddl + "\nLOCATION '" + location + "'"

                with open(table_path, 'w') as f:
                    f.write(new_ddl)

                self.updated_ddls[db + table] = new_ddl
        
    def analyze_performance(self):
        # Print the number of tables updated
        print(f"Number of tables updated: {len(self.updated_ddls)}")
        # Print the number of errors
        print(f"Number of errors: {len(self.errors)}")
        # Print the errors with create view found in ddl
        print("Number of view errors: ", len([i for i in self.errors.values() if "create view found in ddl" in i]))
        # Print the errors with location found in ddl
        print("Number of location errors: ", len([i for i in self.errors.values() if "location found in ddl" in i]))
        
        
def parser():
    parser = argparse.ArgumentParser(description='Update metastore logs')
    parser.add_argument('--metastore_logs', type=str, help='Path to metastore logs', required=True)
    parser.add_argument('--root_bucket', type=str, help='Root bucket name', required=False)
    parser.add_argument('--mount_point', type=str, help='Mount point', required=False)
    parser.add_argument('--database_details_log', type=str, help='Database details log', required=False)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parser()
    updater = MetastoreUpdater(args.metastore_logs, args.root_bucket, args.mount_point, args.database_details_log)
    updater.duplicate_metastore_as_backup()
    updater.update_metastore()
    updater.analyze_performance()