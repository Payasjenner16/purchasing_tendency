import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os

# --------------------------------------
# Load Dataset
# --------------------------------------

# Support relative targeting whether script is run from root or from dl_models directory
csv_path = "static/data/ecommerce_dataset_fixed.csv"
if not os.path.exists(csv_path):
    csv_path = "../static/data/ecommerce_dataset_fixed.csv"

data = pd.read_csv(csv_path)

# Encode categorical IDs
user_encoder = LabelEncoder()
product_encoder = LabelEncoder()
location_encoder = LabelEncoder()

data['user_idx'] = user_encoder.fit_transform(data['user_id'])
data['product_idx'] = product_encoder.fit_transform(data['product_id'])
data['location_idx'] = location_encoder.fit_transform(data['location'])

num_users = data['user_idx'].nunique()
num_products = data['product_idx'].nunique()
num_locations = data['location_idx'].nunique()
