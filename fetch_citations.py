import pandas as pd
import requests
from tqdm import tqdm
import time
import boto3
import os

# === CONFIGURATION ===
INPUT_CSV = "./projectPublications2020.csv"
OUTPUT_FOLDER = "./snapshots"
SNAPSHOT_BATCH_SIZE = 1000
S3_BUCKET_NAME = "my-citations-results-bucket"
MARKER_NOT_FOUND = -1  # Marker for not found DOIs
RATE_LIMIT_DELAY = 0.9  # ~86,400/day
OPENALEX_MAILTO = "sebastian.weiermann@student.kuleuven.be"

# Setup AWS S3 (uses EC2 IAM role or AWS CLI credentials)
s3 = boto3.client("s3")

def upload_snapshot_and_cleanup(snapshot_path, bucket_name, prefix="snapshot_"):
    try:
        # List existing snapshots in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        old_snapshot = None
        if "Contents" in response:
            snapshots = sorted(
                [obj["Key"] for obj in response["Contents"] if obj["Key"].startswith(prefix)]
            )
            if snapshots:
                old_snapshot = snapshots[-1]  # The current most recent one

        # Upload the new snapshot
        snapshot_name = os.path.basename(snapshot_path)
        s3.upload_file(snapshot_path, bucket_name, snapshot_name)
        print(f"Uploaded to S3: {snapshot_name}")

        # Delete old snapshot from S3 only after successful upload
        if old_snapshot and old_snapshot != snapshot_name:
            s3.delete_object(Bucket=bucket_name, Key=old_snapshot)
            print(f"Deleted old snapshot from S3: {old_snapshot}")

        # --- Remove old local snapshots except the current one ---
        local_snapshots = sorted(
            [f for f in os.listdir(OUTPUT_FOLDER) if f.startswith(prefix) and f != snapshot_name]
        )
        for old_local in local_snapshots:
            try:
                os.remove(os.path.join(OUTPUT_FOLDER, old_local))
                print(f"Deleted old local snapshot: {old_local}")
            except Exception as e:
                print(f"Failed to delete local snapshot {old_local}: {e}")

    except Exception as e:
        print(f"Snapshot upload or cleanup failed: {e}")

# === Ensure snapshot folder exists ===
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# === Read CSV ===
df = pd.read_csv(INPUT_CSV, delimiter=";", on_bad_lines="skip", low_memory=False)
df.drop_duplicates(inplace=True)
df.dropna(subset=["projectID", "doi"], inplace=True)
df.reset_index(drop=True, inplace=True)

# === Load existing progress if available ===
progress_file = os.path.join(OUTPUT_FOLDER, "progress.csv")
if os.path.exists(progress_file):
    print("Resuming from previous progress...")
    df_progress = pd.read_csv(progress_file)
    df.loc[df_progress.index, 'citation_count'] = df_progress['citation_count']

# === Citation Fetch Function ===
def fetch_citation_count(doi):
    try:
        doi = doi.strip().lower()
        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto={OPENALEX_MAILTO}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("cited_by_count", 0)
        elif response.status_code == 404:
            return MARKER_NOT_FOUND
        else:
            return MARKER_NOT_FOUND
    except Exception as e:
        print(f"Error fetching DOI {doi}: {e}")
        return MARKER_NOT_FOUND

# === Apply function with snapshot saving ===
results = []
for idx in tqdm(range(len(df))):
    if 'citation_count' in df.columns and not pd.isna(df.at[idx, 'citation_count']):
        continue  # Already processed

    doi = df.at[idx, 'doi']
    citation_count = fetch_citation_count(doi)
    df.at[idx, 'citation_count'] = citation_count
    results.append((idx, citation_count))

    # Save snapshot periodically
    if len(results) % SNAPSHOT_BATCH_SIZE == 0 or idx == len(df) - 1:
        snapshot_path = os.path.join(OUTPUT_FOLDER, f"snapshot_{idx}.csv")
        df.to_csv(snapshot_path, index=False)
        print(f"Saved snapshot: {snapshot_path}")
        try:
            upload_snapshot_and_cleanup(snapshot_path, S3_BUCKET_NAME)
            print(f"Uploaded to S3: {os.path.basename(snapshot_path)}")
        except Exception as e:
            print(f"Failed to upload to S3: {e}")
        # Save minimal progress file
        df[['doi', 'citation_count']].to_csv(progress_file, index=False)

    # Respect API rate limit
    time.sleep(RATE_LIMIT_DELAY)

# === Final save ===
df.to_csv("updated_publications_with_citations.csv", index=False)
s3.upload_file("updated_publications_with_citations.csv", S3_BUCKET_NAME, "updated_publications_with_citations.csv")
print("All done and uploaded.")
