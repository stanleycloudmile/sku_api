import shlex
import subprocess
import json
import pandas as pd
import os

def call_request(url):
    token_command = "gcloud auth print-access-token"
    token_command = shlex.split(token_command)
    access_token = subprocess.run(token_command, capture_output=True, text=True).stdout
    command = f"""curl -X GET -H "Authorization: Bearer {access_token}" "{url}" """
    command = shlex.split(command)
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    
def get_price(sku_id):
    if sku_id == 'not found':
        return str(-1)
    url = f"https://cloudbilling.googleapis.com/v1beta/{sku_id}/price"
    price = call_request(url)
    try:
        ans = price["rate"]["tiers"][0]["listPrice"]["nanos"]
    except KeyError:
        ans = 0
    if len(price["rate"]["tiers"]) != 1:
        print(f"Warning: several tier detected in {sku_id}")
        return price["rate"]["tiers"]
    return str(float(ans)/1000000000)

def get_sku_dict_api():
    sku_dict = {}

    
    Break = False
    first = True
    while (1):
        if first:
            all_skus = call_request("https://cloudbilling.googleapis.com/v2beta/skus?pageSize=5000")
            first = False
        else:
            all_skus = call_request(f"https://cloudbilling.googleapis.com/v2beta/skus?pageSize=5000&pageToken={nextPageToken}")
        try:
            nextPageToken = all_skus["nextPageToken"]
        except:
            Break = True
        all_skus = all_skus['skus']
        for sku in all_skus:
            sku_dict[sku["displayName"]] = sku['name']
        if Break:
            break

        
    a = list(sku_dict.keys())
    b = list(sku_dict.values())
    os.makedirs('data', exist_ok=True)
    with open('data/map.tsv', 'w') as file:
        file.write("name\tsku_id\n")
        for i in range(len(a)):
            file.write(f"{a[i]}\t{b[i]}\n")
    return sku_dict

def get_sku_dict_file(filename):
    df = pd.read_tsv(filename)
    mapping = df.set_index('name')['sku_id'].to_dict()
    return mapping