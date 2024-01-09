import requests

# This script will delete all clusters in a Databricks workspace
# Set the Databricks API endpoint and access token

DATABRICKS_INSTANCE = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().getOrElse(None) 
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)

# Set the API endpoint and access token
api_endpoint = f"https://{DATABRICKS_INSTANCE}/api/2.0/clusters/list"
access_token = DATABRICKS_TOKEN

# Send a GET request to retrieve the list of clusters
response = requests.get(api_endpoint, headers={"Authorization": f"Bearer {access_token}"})

# Check if the request was successful
if response.status_code == 200:
    clusters = response.json()["clusters"]
    print(f"Found {len(clusters)} clusters")
    # Delete each cluster
    for cluster in clusters:
        cluster_id = cluster["cluster_id"]
        delete_endpoint = f"https://{DATABRICKS_INSTANCE}/api/2.0/clusters/delete?cluster_id={cluster_id}"
        delete_response = requests.post(delete_endpoint, headers={"Authorization": f"Bearer {access_token}"})
        
        # Check if the cluster deletion was successful
        if delete_response.status_code == 200:
            print(f"Cluster {cluster_id} deleted successfully")
        else:
            print(f"Failed to delete cluster {cluster_id}")
else:
    print("Failed to retrieve the list of clusters")
