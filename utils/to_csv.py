import pandas as pd
import json
import argparse
import os

def read_log(file_name, checkpoint):
    try:
        with open ("logs/" + checkpoint + "/" + file_name) as f:
            data = f.read().split("\n")
        return data[:-1]

    except FileNotFoundError as e:
        return ''
    except Exception as e:
        print(f"Error while reading {file_name}...")
        return ''

def save_to_csv(data, file_name):
    try:
        pd.DataFrame.from_dict(data).to_csv("./csv/" + file_name)
    except:
        print(f"Error while writing {file_name}...")


def create_instance_profiles(data):
    instance_profile_arn = []
    for d in data:
        try:
            d = json.loads(d)
            instance_profile_arn.append(d['instance_profile_arn'])
        except Exception as e:
            pass
    return {'instance_profile_arn': instance_profile_arn}

def create_instance_pools(data):
    instance_pool_name = []
    instance_pool_id = []

    for d in data:
        try:
            d = json.loads(d)
            instance_pool_name.append(d['instance_pool_name'])
            instance_pool_id.append(d['instance_pool_id'])
        except Exception as e:
            pass

    return {'instance_pool_name': instance_pool_name, 'instance_pool_id': instance_pool_id}

def create_users(data):
    userName = []
    displayName = []

    for d in data:
        try:
            d = json.loads(d)
            if "userName" in d:
                userName.append(d['userName'])
            else:
                userName.append(" ")
            if "displayName" in d:
                displayName.append(d['displayName'])
            else:
                displayName.append(" ")

        except Exception as e:
            pass

    return {'userName': userName, 'displayName': displayName}

def read_group(group_path):
    try:
        with open(group_path) as f:
            data = f.read().split("\n")
        return data
    except FileNotFoundError as e:
        return ''
    except Exception as e:
        print(f"Error while reading {group_path}...")
        print(e)
        return ''

def create_groups(checkpoint = "", directory_name = "groups"):
    groups_path = f"./logs/{checkpoint}/{directory_name}/"
    groups_dir = os.listdir(groups_path)
    groups = {}

    for g in groups_dir:
        group_roles = []
        group_members = []
        group_users = []

        data = read_group(groups_path + g)
        data = data[0]
        d = json.loads(data)
        group_name = d['displayName']

        try:
            roles = d['roles']
            for role in roles:
                group_roles.append(role['value'])
        except:
            pass

        try:
            members = d['members']
            for member in members:
                group_members.append(member['display'])
                group_users.append(member['userName'])
        except:
            pass

        groups[group_name] = [group_roles, group_members, group_users]
    results = {}
    total_names = []
    total_group_roles = []
    total_group_members = []
    total_group_users = []

    for k,v in groups.items():
        total_names.append(k)
        total_group_roles.append(v[0])
        total_group_members.append(v[1])
        total_group_users.append(v[2])
    return {'group_name': total_names, 'group_roles': total_group_roles, 'group_members': total_group_members, 'group_users': total_group_users }


def create_clusters(data):
    cluster_id = []
    cluster_name = []
    creator_user_name = []
    policy_id = []
    instance_profile = []

    for d in data:
        try:
            d = json.loads(d)
            cluster_id.append(d['cluster_id'])
            cluster_name.append(d['cluster_name'])
            creator_user_name.append(d['creator_user_name'])
            if "policy_id" in d.keys():
                policy_id.append(d['policy_id'])
            else:
                policy_id.append(" ")
            try:
                instance_profile.append(d['aws_attributes']['instance_profile_arn'])
            except:
                instance_profile.append('')
        except Exception as e:
            print("Error in creating clusters...")

    return {'cluster_id': cluster_id, 'cluster_name': cluster_name, 'creator_user_name': creator_user_name, 'policy_id': policy_id, 'instance_profile': instance_profile}

def create_jobs(data, jobs_acls):
    job_ids = []
    job_names = []
    job_types = []
    job_creators = []
    job_owners = []
    instance_profile = []

    for d in data:
        try:
            d = json.loads(d)
            job_ids.append(d['job_id'])
            jn = d['settings']['name']
            job_names.append(jn[:jn.index('::')])
            try:
                job_types.append(d['settings']['format'])
            except:
                job_types.append('N/A')
            try:
                job_creators.append(d['creator_user_name'])
            except:
                job_creators.append('N/A')
            try:
                instance_profile.append(d['settings']['new_cluster']['aws_attributes']['instance_profile_arn'])
            except:
                instance_profile.append('')
        except Exception as e:
            print("Error in creating jobs...")

    for a in jobs_acls:
        try:
            a = json.loads(a)
            for j in a['access_control_list']:
                if j.get('user_name', None) != None:
                    if j['all_permissions'][0]['permission_level'] == 'IS_OWNER':
                        job_owners.append(j['user_name'])
        except:
            job_owners.append('')

    return {'job_ids': job_ids, 'job_names': job_names, 'job_type':job_types, 'job_creator':job_creators, 'job_owner': job_owners, 'instance_profile': instance_profile}


def create_shared_logs(checkpoint = "", directory_name = "artifacts/Shared"):
    shared_path = f"./logs/{checkpoint}/{directory_name}"
    notebooks = os.listdir(shared_path)

    return {"notebook_names" : notebooks}

def create_other_artifacts(checkpoint = "", directory_name = "artifacts"):
    other_path = f"./logs/{checkpoint}/{directory_name}"
    notebooks = os.listdir(other_path)
    if "Users" in notebooks:
        notebooks.remove("Users")
    if "Shared" in notebooks:
        notebooks.remove("Shared")

    return {"global_folder_names" : notebooks}

def create_libraries(data):
    library_paths = []
    library_names = []
    for d in data:
        if len(d) > 0:
            try:
                d = json.loads(d)
                library_paths.append(d['path'])
                library_names.append(d['path'].split("/")[-1])
            except Exception as e:
                print("Error in creating libraries...")

    return {'library_paths': library_paths, 'library_names': library_names}

def create_scopes(checkpoint = "", directory_name = "secret_scopes"):
    try:
        secrets = os.listdir(f"./logs/{checkpoint}/{directory_name}/")
        return {"secret_scopes" : secrets}
    except:
        print("Error while reading secrets directory...")

def create_mounts(data):
    mount_paths = []
    mount_sources = []

    for d in data:
        try:
            d = json.loads(d)
            mount_paths.append(d['path'])
            mount_sources.append(d['source'])
        except Exception as e:
            print("Error in mounts...")

    return { 'mount_paths' : mount_paths, 'mount_sources' : mount_sources }


def create_metastore(checkpoint = "", directory_name = 'metastore'):
    metastore_path = f"./logs/{checkpoint}/{directory_name}"
    metastore_database = [i for i in os.listdir(metastore_path)]

    return {'metastore_database' : metastore_database}
