import os
import sys
import json
import argparse
import logging
import time
import math
from pathlib import Path
from multiprocessing import Pool, cpu_count, Manager
from functools import partial

# --- Configuration Check ---
# Check if PROJECT_ROOT is set, needed for imports if not running from root
if "PROJECT_ROOT" not in os.environ:
    # Try to determine PROJECT_ROOT relative to this script
    # Script location: tests/Supramolecular/src/final/
    try:
        SCRIPT_DIR = Path(__file__).resolve().parent
        SRC_ROOT = SCRIPT_DIR.parent # tests/Supramolecular/src/
        TESTS_ROOT = SRC_ROOT.parent # tests/Supramolecular/
        PROJECT_ROOT_GUESS = TESTS_ROOT.parent.parent # Chem-Ontology-Constructor/
        if (PROJECT_ROOT_GUESS / 'config' / 'settings.py').exists():
             print(f"PROJECT_ROOT environment variable not set. Guessing: {PROJECT_ROOT_GUESS}")
             os.environ['PROJECT_ROOT'] = str(PROJECT_ROOT_GUESS)
             sys.path.insert(0, str(PROJECT_ROOT_GUESS)) # Prepend to path
        else:
             raise FileNotFoundError("Could not reliably guess PROJECT_ROOT.")
    except Exception as e:
        print(f"Error: PROJECT_ROOT environment variable not set and could not be reliably guessed. {e}")
        print("Please set the PROJECT_ROOT environment variable to the absolute path of 'Chem-Ontology-Constructor'.")
        sys.exit(1)
else:
    # Ensure the existing PROJECT_ROOT is in the path if needed
    project_root_path = os.environ['PROJECT_ROOT']
    if project_root_path not in sys.path:
         sys.path.insert(0, project_root_path)

# --- Imports ---
# Now import project modules
try:
    import dspy
    # from autology_constructor.modules import ChemOntology # Old import, to be removed by a subsequent one
    from autology_constructor.modules import chemonto_refined, chemonto_base # New imports
    # from autology_constructor.assertions import (
    #     chemonto_with_entities_assertions,
    #     chemonto_with_elements_assertions,
    #     chemonto_with_data_properties_assertions,
    #     chemonto_with_object_properties_assertions
    # ) # Removed old assertion-based modules
    from autology_constructor.ontology_merge import merge_ontology
    from autology_constructor.preprocess import create_metadata_properties
    from config import settings # For LLM_CONFIG and OPENAI_API_KEY
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print(f"PROJECT_ROOT is currently set to: {os.environ.get('PROJECT_ROOT', 'Not Set')}")
    print("Ensure PROJECT_ROOT environment variable is set correctly and points to 'Chem-Ontology-Constructor'.")
    print("Also ensure required packages (like dspy) are installed in your environment.")
    sys.exit(1)

# --- Logging Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(processName)s - %(message)s')
logger = logging.getLogger('ontology_builder')
logger.setLevel(logging.INFO) # Default level

# File Handler
log_file = Path(__file__).parent / 'ontology_builder.log'
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO) # Console shows INFO and above
logger.addHandler(console_handler)

# --- Argument Parser Setup ---
def setup_arg_parser():
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Builds an ontology from text chunks using DSPy.")
    parser.add_argument("--input-path", type=str, required=True, help="Path to the directory containing input text files (chunks).")
    parser.add_argument("--output-path", type=str, default="./build", help="Path to the directory where ontology files will be saved.")
    # parser.add_argument("--components", type=str, nargs='*', help="List of ontology components to generate (e.g., entities elements data_properties object_properties). Extracts all if not specified.")
    parser.add_argument("--max-workers", type=int, default=cpu_count(), help="Maximum number of worker processes for parallel processing.")
    parser.add_argument("--parallel", action='store_true', help="Enable parallel processing. If not set, runs sequentially.")
    parser.add_argument("--cpu-fraction", type=float, default=0.7,
                        help="Fraction of CPU cores to use when parallel processing is enabled (e.g., 0.7 for 70%).")
    parser.add_argument("--debug", action='store_true', default=False,
                        help="Enable debug logging.")
    parser.add_argument('--extractor-type', choices=['refined', 'base'], default='refined',
                        help="Type of extractor to use: 'refined' (with dspy.Refine) or 'base' (without).")
    return parser

# --- DSPy LM Setup ---
def setup_dspy_lm():
    """Sets up and configures the DSPy Language Model."""
    try:
        logger.info("Setting up DSPy LM...")
        lm = dspy.LM('openai/gpt-4.1', temperature=0, max_tokens=10000)
        dspy.configure(lm=lm)
        teacher = dspy.LM("openai/gpt-4o",temperature=1)
    except Exception as e:
        logger.exception("Failed to set up DSPy LM.")
        raise

# --- Worker Function ---
# NOTE: DSPy LM configuration needs to happen *within* the worker process
# if it's not automatically inherited or if using certain multiprocessing start methods.
# Configuring it globally *before* the pool is created might work for 'fork' but not 'spawn'.
# A safer approach is to re-configure within the worker or pass necessary config.

def process_chunk_worker(worker_args):
    """
    Processes a single chunk to generate ontology components.
    Designed to be run in a separate process.
    """
    chunk_index, chunk_data, components_list, extractor_type = worker_args
    process_name = f"Worker-{os.getpid()}" # Identify worker in logs
    logger = logging.getLogger('ontology_builder') # Get logger configured in main process

    logger.info(f"Processing chunk {chunk_index}...")
    try:
        setup_dspy_lm()
    except Exception as e:
        logger.critical("Failed to initialize DSPy LM. Exiting.")
        return
    # Re-configure DSPy LM within the worker process for safety/compatibility
    # setup_dspy_lm() # Might be needed depending on start method and dspy internals

    content = chunk_data.get("content", "")
    source = chunk_data.get("source", "UnknownSource")
    if not content:
        logger.warning(f"Chunk {chunk_index} has empty content. Skipping generation.")
        return {'index': chunk_index, 'source': source, 'error': 'Empty content'}

    results = {'index': chunk_index, 'source': source}
    temp_entities_result = None # To hold result for dependency

    try:
        start_time = time.time()

        active_extractor = None
        if extractor_type == 'refined':
            active_extractor = chemonto_refined
            logger.debug(f"Chunk {chunk_index}: Using refined extractor.")
        else: # extractor_type == 'base'
            active_extractor = chemonto_base
            logger.debug(f"Chunk {chunk_index}: Using base extractor.")

        if not active_extractor:
            logger.error(f"Chunk {chunk_index}: Could not determine active extractor for type '{extractor_type}'.")
            results['error'] = f"Invalid extractor type: {extractor_type}"
            return results

        logger.debug(f"Chunk {chunk_index}: Generating ontology components with {extractor_type} extractor...")
        prediction = active_extractor(context=content)
        results['ontology_prediction'] = prediction
        logger.debug(f"Chunk {chunk_index}: Ontology components generation finished.")

        end_time = time.time()
        logger.info(f"Chunk {chunk_index} processed successfully in {end_time - start_time:.2f} seconds.")

    except Exception as e:
        logger.exception(f"Chunk {chunk_index}: Error during processing.")
        results['error'] = str(e)

    return results


# --- Main Execution Logic ---
def main(args):
    """Main function to orchestrate the ontology building process."""
    if args.debug:
        logger.setLevel(logging.DEBUG)
        # Update console handler level too if needed, or rely on file for debug logs
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")

    # try:
    #     setup_dspy_lm()
    # except Exception as e:
    #     logger.critical("Failed to initialize DSPy LM. Exiting.")
    #     return # Exit if LM setup fails

    logger.info("Initializing main ontology...")
    try:
        # Pass base_iri if required by ChemOntology or merge_ontology
        # For now, assume default constructor works and merge handles IRI/saving
        # extractor = ChemOntology()
        create_metadata_properties() # Pass the instance
        logger.info("Main ontology initialized and metadata added.")
    except Exception as e:
        logger.exception("Failed to initialize ChemOntology or add metadata.")
        return

    # --- Input Data Handling ---
    input_path = Path(args.input_path)
    all_chunks_data = []
    json_files_to_process = []

    if input_path.is_file() and input_path.suffix.lower() == ".json":
        json_files_to_process.append(input_path)
    elif input_path.is_dir():
        logger.info(f"Scanning directory: {input_path}")
        for item in input_path.iterdir():
            if item.is_file() and item.suffix.lower() == ".json":
                json_files_to_process.append(item)
    else:
        logger.error(f"Invalid input path: {args.input_path}. Must be a JSON file or a directory containing JSON files.")
        return

    if not json_files_to_process:
        logger.warning("No JSON files found to process.")
        return

    logger.info(f"Found {len(json_files_to_process)} JSON file(s) to process.")

    # Read chunks iteratively
    total_chunks_read = 0
    for json_file in json_files_to_process:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                chunks_in_file = json.load(f)
                if isinstance(chunks_in_file, list):
                    # Add file source info if needed, otherwise rely on chunk['source']
                    # for i, chunk in enumerate(chunks_in_file):
                    #     chunk['_file_source'] = json_file.name # Example
                    all_chunks_data.extend(chunks_in_file)
                    logger.debug(f"Read {len(chunks_in_file)} chunks from {json_file.name}")
                    total_chunks_read += len(chunks_in_file)
                else:
                    logger.warning(f"Skipping {json_file.name}: Content is not a JSON list.")
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {json_file.name}. Skipping.")
        except Exception as e:
            logger.exception(f"Error reading file {json_file.name}.")

    if not all_chunks_data:
        logger.error("No valid chunks found in the specified input path(s).")
        return

    logger.info(f"Total chunks to process: {len(all_chunks_data)}")

    all_components = ['entities', 'elements', 'data_properties', 'object_properties'] # Keep for reference, but not for selection

    # if not args.components:
    #     logger.info("No specific components requested, defaulting to all components for structure, but extraction is now unified.")
        # args.components = all_components # No longer needed to set this for worker
    # else:
        # logger.info(f"Requested components: {args.components}")
        # # Validate requested components
        # for comp in args.components:
        #     if comp not in all_components:
        #         logger.error(f"Invalid component specified: {comp}. Valid components are: {all_components}")
        #         return

    # --- Task Preparation ---
    # tasks = [(idx, chunk, args.components, args.extractor_type) for idx, chunk in enumerate(all_chunks_data)] # Old tasks with components
    tasks = [(idx, chunk, all_components, args.extractor_type) for idx, chunk in enumerate(all_chunks_data)] # Pass all_components for reference if needed by worker, or an empty list if not

    # results_list = [] # This list will not be used for merging anymore if we merge on the fly
    overall_processing_start_time = time.time() # Renamed from start_processing_time
    merge_success_count = 0
    merge_fail_count = 0
    chunks_processed_since_last_save = 0
    save_batch_size = 100 # Configurable batch size for saving

    # --- Execution (Parallel or Sequential) ---
    if args.parallel:
        if len(tasks) == 0:
             logger.info("No tasks to run in parallel.")
        else:
            try:
                fraction = max(0.1, min(1.0, args.cpu_fraction)) # Ensure fraction is reasonable
                num_processes = max(1, math.floor(cpu_count() * fraction))
                logger.info(f"Starting parallel processing with {num_processes} worker(s)...")

                with Pool(processes=num_processes) as pool:
                    # Using imap_unordered to get results as they complete
                    for result_dict in pool.imap_unordered(process_chunk_worker, tasks):
                        idx = result_dict.get('index', -1)
                        if 'error' in result_dict:
                            logger.error(f"Skipping merge for chunk {idx} due to processing error: {result_dict['error']}")
                            merge_fail_count += 1
                            continue
                        
                        # logger.info(f"Attempting to merge results for chunk {idx}...") # Log level might be too verbose here now
                        try:
                            prediction = result_dict.get('ontology_prediction')
                            source_info = result_dict.get('source', f"Source_Chunk_{idx}")

                            if not prediction:
                                logger.error(f"No ontology prediction found for chunk {idx}. Skipping merge.")
                                merge_fail_count += 1
                                continue
                            
                            merge_ontology(
                                prediction.ontology_entities,
                                prediction.ontology_elements,
                                prediction.ontology_data_properties,
                                prediction.ontology_object_properties,
                                source_info,
                                "", # Placeholder for file_path, ensure merge_ontology handles this or update if needed
                                save_after_merge=False # Explicitly set to False
                            )
                            # logger.info(f"Successfully merged chunk {idx} into memory.") # Log level might be too verbose
                            merge_success_count += 1
                            chunks_processed_since_last_save += 1

                            if chunks_processed_since_last_save >= save_batch_size:
                                settings.ONTOLOGY_SETTINGS.ontology.save()
                                logger.info(f"批处理保存本体... ({chunks_processed_since_last_save} chunks merged since last save)")
                                time.sleep(1)
                                chunks_processed_since_last_save = 0
                        except Exception as e:
                            logger.exception(f"Error merging results for chunk {idx} during parallel processing.")
                            merge_fail_count += 1
                logger.info("Parallel processing and merging finished.")
            except Exception as e:
                 logger.exception("Error during parallel processing setup or execution.")
                 # Potentially handle partial results or exit
                 return
    else:
        logger.info("Starting sequential processing and merging...")
        for i, task in enumerate(tasks):
            logger.info(f"Processing task {i+1}/{len(tasks)} sequentially...")
            result_dict = process_chunk_worker(task)
            
            idx = result_dict.get('index', -1)
            if 'error' in result_dict:
                logger.error(f"Skipping merge for chunk {idx} due to processing error: {result_dict['error']}")
                merge_fail_count += 1
                continue

            # logger.info(f"Attempting to merge results for chunk {idx}...") # Log level might be too verbose
            try:
                prediction = result_dict.get('ontology_prediction')
                source_info = result_dict.get('source', f"Source_Chunk_{idx}")

                if not prediction:
                    logger.error(f"No ontology prediction found for chunk {idx}. Skipping merge.")
                    merge_fail_count += 1
                    continue

                merge_ontology(
                    prediction.ontology_entities,
                    prediction.ontology_elements,
                    prediction.ontology_data_properties,
                    prediction.ontology_object_properties,
                    source_info,
                    "", # Placeholder for file_path
                    save_after_merge=False # Explicitly set to False
                )
                # logger.info(f"Successfully merged chunk {idx} into memory.") # Log level might be too verbose
                merge_success_count += 1
                chunks_processed_since_last_save += 1

                if chunks_processed_since_last_save >= save_batch_size:
                    settings.ONTOLOGY_SETTINGS.ontology.save()
                    logger.info(f"批处理保存本体... ({chunks_processed_since_last_save} chunks merged since last save)")
                    time.sleep(1)
                    chunks_processed_since_last_save = 0
            except Exception as e:
                logger.exception(f"Error merging results for chunk {idx} during sequential processing.")
                merge_fail_count += 1
        logger.info("Sequential processing and merging finished.")

    # Final save for any remaining chunks
    if chunks_processed_since_last_save > 0:
        settings.ONTOLOGY_SETTINGS.ontology.save()
        logger.info(f"最终保存剩余的本体更改... ({chunks_processed_since_last_save} chunks)")
        chunks_processed_since_last_save = 0 # Reset just in case

    overall_processing_end_time = time.time()
    # logger.info(f"Chunk processing phase took {end_processing_time - start_processing_time:.2f} seconds.") # Removed

    # --- Merge Results ---
    # logger.info("Merging results into the main ontology...") # Removed, merging is done above
    # merge_success_count = 0 # Moved up
    # merge_fail_count = 0 # Moved up
    # merge_start_time = time.time() # Removed

    # Results list should be ordered correctly from map or sequential loop # Comment no longer fully applies
    # for result_dict in results_list: # This loop is removed
    #     idx = result_dict.get('index', -1)
    #     if 'error' in result_dict:
    #         logger.error(f"Skipping merge for chunk {idx} due to processing error: {result_dict['error']}")
    #         merge_fail_count += 1
    #         continue
    #
    #     logger.debug(f"Merging results for chunk {idx}...")
    #     try:
    #         # Extract results safely
    #         prediction = result_dict.get('ontology_prediction')
    #         source = result_dict.get('source', f"Source_Chunk_{idx}")
    #
    #         # Call merge_ontology - assuming it modifies main_ontology in place
    #         # and handles saving/output internally based on its logic.
    #         merge_ontology(
    #             prediction.ontology_entities,
    #             prediction.ontology_elements,
    #             prediction.ontology_data_properties,
    #             prediction.ontology_object_properties,
    #             source,
    #             "" # Placeholder for potential future argument?
    #         )
    #         logger.debug(f"Successfully merged chunk {idx}.")
    #         merge_success_count += 1
    #     except Exception as e:
    #         logger.exception(f"Error merging results for chunk {idx}.")
    #         merge_fail_count += 1

    # merge_end_time = time.time() # Removed
    # logger.info(f"Merging phase took {merge_end_time - merge_start_time:.2f} seconds.") # Removed
    logger.info(f"Merge summary: {merge_success_count} succeeded, {merge_fail_count} failed.")
    logger.info("Ontology building process finished.")
    total_time = overall_processing_end_time - overall_processing_start_time # Adjusted
    logger.info(f"Total execution time: {total_time:.2f} seconds.")

# --- Main Program Entry Point ---
if __name__ == "__main__":
    parser = setup_arg_parser()
    args = parser.parse_args()
    main(args) 