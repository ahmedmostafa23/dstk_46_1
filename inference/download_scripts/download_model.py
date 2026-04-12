from google.cloud import storage
from google.oauth2 import service_account

bucket_name = "dstk-46-bucket"
source_blob_name = "models/best_recall_catboost.pkl"
local_file_path = "models/best_recall_catboost.pkl"

client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(source_blob_name)
blob.download_to_filename(local_file_path)
