import pandas as pd
import subprocess
import shlex
import json
import csv
from utils import *
import os



# Read the Excel file
df = pd.read_csv('data/source.csv')

# Print the first 5 rows
print(df.head())

# sku_dict = get_sku_dict_file("map.csv")
sku_dict = get_sku_dict_api()

df["SKU_ID"] = df["Product"].map(sku_dict).fillna('not found')
df["Price"] = df["SKU_ID"].apply(get_price)

os.makedirs('result', exist_ok=True)
df.to_csv('result/result.csv', index=False)