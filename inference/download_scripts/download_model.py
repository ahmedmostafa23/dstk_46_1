import os
from google.cloud import storage

bucket_name = os.environ["GCS_BUCKET_NAME"]
source_blob_name = os.environ["GCS_MODEL_PATH"]
local_file_path = "models/model.pkl"

client = storage.Client()
bucket = client.bucket(bucket_name)
blob = bucket.blob(source_blob_name)
blob.download_to_filename(local_file_path)
