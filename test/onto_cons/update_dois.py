import os
import json
import logging
import argparse
from typing import Dict

# --- Configuration Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Default location relative to the script
DEFAULT_DOI_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../data/IDA/DOI'))
DEFAULT_CHUNKS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../data/IDA/chunks'))
DEFAULT_MAPPING_FILE = os.path.join(DEFAULT_DOI_DIR, 'doi_mapping.json')
LOG_FILE = os.path.join(SCRIPT_DIR, 'doi_update.log')
DOI_MISSING_PLACEHOLDER = "DOI_MISSING" # Should match the one in pdf_chunk_processor.py

# --- Logger Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
update_logger = logging.getLogger('doi_updater')
update_logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not update_logger.handlers:
    # File handler
    file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    update_logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    update_logger.addHandler(console_handler)

# --- Core Function ---
def update_dois_in_chunks(chunks_dir: str, mapping_file_path: str) -> None:
    """
    Reads a JSON mapping file and updates the 'source' field in chunk JSON files
    where the source is currently the placeholder.
    """
    update_logger.info("--- Starting DOI Update Process ---")
    update_logger.info(f"Reading mapping file: {mapping_file_path}")

    # 1. Read DOI Mapping
    try:
        with open(mapping_file_path, 'r', encoding='utf-8') as f:
            doi_mapping: Dict[str, str] = json.load(f)
        update_logger.info(f"Successfully loaded {len(doi_mapping)} mappings.")
    except FileNotFoundError:
        update_logger.error(f"Error: Mapping file not found at {mapping_file_path}. Exiting.")
        return
    except json.JSONDecodeError as e:
        update_logger.error(f"Error: Could not decode JSON from mapping file {mapping_file_path}: {e}. Exiting.")
        return
    except Exception as e:
        update_logger.error(f"An unexpected error occurred reading mapping file: {e}", exc_info=True)
        return

    # 2. Iterate through Chunk Files
    update_logger.info(f"Scanning chunk directory: {chunks_dir}")
    updated_files_count = 0
    processed_files_count = 0
    skipped_files_count = 0

    try:
        for filename in os.listdir(chunks_dir):
            if filename.lower().endswith('.json'):
                processed_files_count += 1
                file_key = os.path.splitext(filename)[0] # Get filename without extension
                json_path = os.path.join(chunks_dir, filename)

                if file_key not in doi_mapping:
                    update_logger.debug(f"Skipping {filename}: No mapping found for key '{file_key}'.")
                    skipped_files_count += 1
                    continue

                actual_doi = doi_mapping[file_key]
                if not actual_doi: # Skip if mapped DOI is empty
                     update_logger.warning(f"Skipping {filename}: Mapping for '{file_key}' has an empty DOI.")
                     skipped_files_count += 1
                     continue

                update_logger.debug(f"Processing {filename} with DOI: {actual_doi}")
                file_updated = False
                try:
                    # Read the JSON chunk file
                    with open(json_path, 'r', encoding='utf-8') as f_in:
                        chunks_data: List[Dict[str, Any]] = json.load(f_in)

                    # Update source field if it's the placeholder
                    for chunk in chunks_data:
                        if chunk.get('source') == DOI_MISSING_PLACEHOLDER:
                            chunk['source'] = actual_doi
                            file_updated = True

                    # Write back only if changes were made
                    if file_updated:
                        with open(json_path, 'w', encoding='utf-8') as f_out:
                            json.dump(chunks_data, f_out, ensure_ascii=False, indent=4)
                        update_logger.info(f"Updated DOI in {filename} to '{actual_doi}'.")
                        updated_files_count += 1
                    else:
                        update_logger.debug(f"No DOI placeholder found in {filename}. No update needed.")
                        skipped_files_count += 1

                except json.JSONDecodeError as e:
                    update_logger.error(f"Error decoding JSON in {filename}: {e}. Skipping file.")
                    skipped_files_count += 1
                except IOError as e:
                    update_logger.error(f"Error reading/writing {filename}: {e}. Skipping file.")
                    skipped_files_count += 1
                except Exception as e:
                    update_logger.error(f"Unexpected error processing {filename}: {e}. Skipping file.", exc_info=True)
                    skipped_files_count += 1

    except FileNotFoundError:
         update_logger.error(f"Error: Chunks directory not found at {chunks_dir}. Exiting.")
         return
    except Exception as e:
        update_logger.error(f"An error occurred listing files in chunks directory: {e}", exc_info=True)
        return

    update_logger.info("--- DOI Update Process Finished ---")
    update_logger.info(f"Total JSON files scanned: {processed_files_count}")
    update_logger.info(f"Files successfully updated: {updated_files_count}")
    update_logger.info(f"Files skipped (no mapping, empty DOI, or no placeholder found): {skipped_files_count}")
    update_logger.info(f"Logs saved to: {LOG_FILE}")

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update DOI placeholders in chunk JSON files using a mapping file.")
    parser.add_argument("--chunks-dir", default=DEFAULT_CHUNKS_DIR,
                        help=f"Directory containing the chunk JSON files (default: {DEFAULT_CHUNKS_DIR})")
    parser.add_argument("--mapping-file", default=DEFAULT_MAPPING_FILE,
                        help=f"Path to the JSON file mapping PDF filenames (without ext) to DOIs (default: {DEFAULT_MAPPING_FILE})")

    args = parser.parse_args()

    # Ensure the DOI directory exists before attempting to read the mapping file
    mapping_dir = os.path.dirname(args.mapping_file)
    if not os.path.exists(mapping_dir):
         print(f"Warning: Directory for mapping file does not exist: {mapping_dir}")
         # Optionally create it? Or just let the file open fail?
         # os.makedirs(mapping_dir, exist_ok=True)

    update_dois_in_chunks(args.chunks_dir, args.mapping_file) 