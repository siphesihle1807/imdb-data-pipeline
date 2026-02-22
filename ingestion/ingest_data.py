# Imports 

import os
import requests
from pathlib import Path
from google.cloud import storage, bigquery


# Env config 
PROJECT_ID = os.getenv("GCP_PROJECT")
BUCKET_NAME = os.getenv("GCS_BUCKET")
DATASET_NAME = os.getenv("BQ_DATASET")

# Link to datasets and files to be downloaded. 
IMDB_BASE_URL = "https://datasets.imdbws.com/"

DATASETS = [
    "title.basics.tsv.gz",
    "title.ratings.tsv.gz",
    "name.basics.tsv.gz"
]

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def download_data(filename: str) -> Path:
    url = IMDB_BASE_URL + filename
    local_path = DOWNLOAD_DIR / filename

    print(f"Downloading {filename}...")

    with requests.get(url, stream=True) as req:
        req.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in req.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"Downloaded to: {local_path}")
    return local_path



# upload data to GCS

def upload_to_gcs(local_path: Path) -> str:
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)

    blob_path = f"raw/imdb/{local_path.stem}/{local_path.name}"
    blob = bucket.blob(blob_path)

    print(f"Uploading {local_path.name} to Google Storage")
    blob.upload_from_filename(local_path)

    print(f"Uploaded to gs://{BUCKET_NAME}/{blob_path}")
    return f"gs://{BUCKET_NAME}/{blob_path}"


# Load to BQ
def load_to_bq(gcs_uri: str, table_name):
    client = bigquery.Client(project=PROJECT_ID)

    dataset_id = f"{PROJECT_ID}.{DATASET_NAME}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = "US"
    client.create_dataset(dataset, exists_ok=True) 
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV, 
        skip_leading_rows=1, 
        autodetect=True, 
        field_delimiter="\t", 
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, 
        quote_character=""
    )

    print(f"Loading table {table_name} into BigQuery.")
    load_job = client.load_table_from_uri(
        gcs_uri, 
        table_id, 
        location="US",
        job_config=job_config,
    )

    load_job.result()  

    table = client.get_table(table_id)
    print(f"Loaded {table.num_rows} rows into {table_name}.")


# Process individual datasets
def process_dataset(filename: str):
    local_path = download_data(filename)
    gcs_uri = upload_to_gcs(local_path)

    table_name = filename.replace(".tsv.gz", "").replace(".", "_")
    load_to_bq(gcs_uri, table_name)


# execution
def main():
    if not all([PROJECT_ID, BUCKET_NAME, DATASET_NAME]):
        raise ValueError("Missing required environment variables.")
    
    for dataset in DATASETS:
        process_dataset(dataset)

    print("Ingestion complete.")


if __name__ == "__main__":
    main()