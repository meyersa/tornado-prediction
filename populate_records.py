"""
Script to download records from Zenodo and upload them to Backblaze S3

(Zenodo was being very slow)
"""
import os
import tempfile
import subprocess
import logging

TORNET_FILE_PATH = os.getenv("FILE_PATH", "./tornet_files.txt")
BUCKET = os.getenv("APP", "TorNetBecauseZenodoSlow")

# Set up logging
logging.basicConfig(level=logging.INFO)


def download_links(links):
    """
    Download files from the provided links using aria2c.
    Creates a temporary file for links and deletes it after use.
    """
    temp_file = None
    try:
        # Create a temporary file with links
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        temp_file.writelines(link + '\n' for link in links)
        temp_file.close()
        logging.info(f"Temporary file created: {temp_file.name}")

        # Run aria2c to download files
        logging.info(f"Starting downloads for links: {', '.join(links)}")
        command = ["./venv/bin/aria2c", "-j", "3", "-x", "16", "-s", "16", "-i", temp_file.name]
        subprocess.run(command, check=True)
        logging.info("Downloads completed successfully.")
    except Exception as e:
        logging.error(f"Error during download: {e}")
        exit(1)
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
            logging.info(f"Temporary file deleted: {temp_file.name}")


def upload_files(file_list):
    """
    Upload files to Backblaze B2 using the b2 CLI.
    """
    for file in file_list:
        command = ["./venv/bin/b2", "file", "upload", BUCKET, file, file]
        try:
            logging.info(f"Uploading '{file}' to B2...")
            subprocess.run(command, check=True)
            logging.info(f"File '{file}' uploaded successfully.")
        except Exception as e:
            logging.error(f"Failed to upload '{file}': {e}")
            exit(1)


def delete_files(file_list):
    """
    Delete specified files from the local system.
    """
    for file in file_list:
        try:
            os.remove(file)
            logging.info(f"Deleted file: {file}")
        except OSError as e:
            logging.warning(f"Failed to delete file '{file}': {e}")


def main():
    """
    Main function to process links in batches.
    Ensures files are downloaded, uploaded, and cleaned up.
    """
    if not os.path.isfile(TORNET_FILE_PATH):
        logging.error(f"The file '{TORNET_FILE_PATH}' does not exist.")
        exit(1)

    try:
        # Read all links from the file
        with open(TORNET_FILE_PATH, 'r') as file:
            links = [line.strip() for line in file if line.strip()]

        if not links:
            logging.error("No links found in the file.")
            exit(1)

        # Process links in batches
        batch_size = 3
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            logging.info(f"Processing batch {i // batch_size + 1}: {batch}")

            # Download files for the current batch
            download_links(batch)

            # Determine filenames from links for upload and cleanup
            downloaded_files = [os.path.basename(link) for link in batch]

            # Upload downloaded files to B2
            upload_files(downloaded_files)

            # Clean up local files
            delete_files(downloaded_files)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()