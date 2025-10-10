import os
import json
import logging
import re
import argparse
from typing import Optional, List, Dict, Any

# Attempt imports, handle if not found
try:
    from docling.document_converter import DocumentConverter, ConversionResult
    from docling.chunking import HybridChunker
    # Attempt to import the necessary tokenizer class
    # from transformers import AutoTokenizer # If using HF tokenizer
    import tiktoken # If using tiktoken
except ImportError as e:
    print(f"Error: Required libraries not found ({e}).")
    print("Please install them: pip install 'docling-core[chunking]' PyPDF2 tiktoken")
    # If using HF Tokenizer, add: transformers
    exit(1)

try:
    import PyPDF2
except ImportError:
    print("Error: PyPDF2 library not found.")
    print("Please install it: pip install PyPDF2")
    exit(1)

# --- Configuration Constants ---
# Assuming the script is in tests/Supramolecular/src/final/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..')) # Go up one level to src
TESTS_ROOT = os.path.abspath(os.path.join(SRC_ROOT, '..')) # Go up one level to Supramolecular
PROJECT_ROOT = os.path.abspath(os.path.join(TESTS_ROOT, '../../')) # Go up two levels to Chem-Ontology-Constructor

PDF_DIR = os.path.join(PROJECT_ROOT, r'data\pdfs')
CHUNKS_DIR = os.path.join(PROJECT_ROOT, r'data\processed_texts')
DOI_DIR = os.path.join(PROJECT_ROOT, r'data\DOI') # Directory for mapping file
LOG_FILE = os.path.join(SCRIPT_DIR, 'processing.log') # Place log in the same dir as the script
DOI_MISSING_PLACEHOLDER = "DOI_MISSING"

# Use o200k_base tokenizer associated with GPT-4o/GPT-4.1
TOKENIZER_ENCODING = "o200k_base"
MAX_CHUNK_TOKENS = 800 # Updated from 4096 to approximate 3000 chars with default tokenizer

# DOI Regex (common pattern)
DOI_REGEX = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b") # Added word boundaries

# --- Filtering Constants (Adjusted Plan) ---
NON_MAIN_HEADERS = {
    'references', 'acknowledgements', 'acknowledgments', 'funding', 'author contributions',
    'conflicts of interest', 'conflict of interest', 'competing interests',
    'copyright', 'citation', 'received', 'accepted', 'published', 'edited by',
    'reviewed by', 'correspondence', 'supplementary material',
    'open access', 'data availability', "publisher's note", "publisher s note"
    # 'keywords', 'abstract' REMOVED FROM THIS SET based on user feedback
    # Can add more specific, unambiguous non-main headers if needed
}
# Adjusted patterns: Removed et al. pattern to be more conservative
NON_MAIN_PATTERNS = [
    re.compile(r'\(\d{4}\).*(doi:|doi\.org/)'), # Reference with year and doi (strong indicator)
    re.compile(r'©\s*\d{4}'), # Copyright symbol + year
    re.compile(r'declare that .* conflict of interest', re.IGNORECASE | re.DOTALL),
    re.compile(r'supported by', re.IGNORECASE),
    re.compile(r'All authors contributed|author contributions', re.IGNORECASE)
]

# --- Logger Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('pdf_processor')
logger.setLevel(logging.DEBUG) # Log DEBUG messages and above

# Prevent duplicate handlers if script is run multiple times in same session (e.g., in some IDEs)
if not logger.handlers:
    # File handler for all logs
    file_handler = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG) # Log everything to file
    logger.addHandler(file_handler)

    # Console handler for progress (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

# --- Helper Functions ---

def get_chunker() -> Optional[HybridChunker]:
    """Initializes and returns the HybridChunker."""
    try:
        # Get the tiktoken encoding object - REMOVED
        # tokenizer_obj = tiktoken.get_encoding(TOKENIZER_ENCODING)

        # HybridChunker expects a Hugging Face compatible tokenizer interface.
        # We need to check if docling internally handles tiktoken objects or if we need a wrapper.
        # For now, assuming it might require a specific interface or name.
        # Let's try passing the tiktoken object directly first, but prepare for fallback.

        # TODO: Verify if HybridChunker directly accepts tiktoken encoding object.
        # If not, a wrapper like below might be needed, or find a compatible HF tokenizer.
        # class TiktokenWrapper:
        #     def __init__(self, encoding):
        #         self.encoding = encoding
        #     def encode(self, text, **kwargs):
        #         return self.encoding.encode(text, **kwargs)
        #     def decode(self, tokens, **kwargs):
        #         return self.encoding.decode(tokens, **kwargs)
        #     def tokenize(self, text, **kwargs):
        #          # HybridChunker might call tokenize - ensure this returns list of strings if needed
        #          encoded = self.encoding.encode(text, **kwargs)
        #          return [self.encoding.decode_single_token_bytes(token).decode('utf-8', errors='replace') for token in encoded]
        #     # Add other methods HybridChunker might call (e.g., vocab_size, model_max_length if needed)
        #     @property
        #     def model_max_length(self):
        #          return MAX_CHUNK_TOKENS # Or derive from model if possible

        # tokenizer_wrapped = TiktokenWrapper(tokenizer_obj)

        # Use default tokenizer by removing the tokenizer argument
        chunker = HybridChunker(
            # tokenizer=tokenizer_obj, # Pass tiktoken object directly - REMOVED
            max_tokens=MAX_CHUNK_TOKENS,
            merge_peers=True
        )
        # Updated log message for default tokenizer
        logger.info(f"Initialized HybridChunker with default tokenizer and max_tokens={MAX_CHUNK_TOKENS}")
        return chunker
    except ValueError as ve:
         logger.error(f"ValueError initializing HybridChunker, potentially tokenizer issue: {ve}")
         logger.error(f"Consider if HybridChunker needs a HuggingFace tokenizer name/object instead of '{TOKENIZER_ENCODING}'.")
         return None
    except Exception as e:
        logger.error(f"Failed to initialize HybridChunker: {e}", exc_info=True)
        return None

def extract_doi(pdf_path: str, conversion_result: Optional[ConversionResult] = None) -> Optional[str]:
    """
    Attempts to extract DOI from PDF metadata or text.
    Priority: PyPDF2 Meta -> Docling Meta (if available) -> Regex on Text.
    """
    pdf_filename = os.path.basename(pdf_path)
    # 1. Try PyPDF2 Metadata
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f, strict=False) # Use strict=False for potentially problematic PDFs
            metadata = reader.metadata
            if metadata and '/DOI' in metadata:
                doi = metadata['/DOI']
                # Clean up potential prefixes/suffixes if it's not a simple string
                if isinstance(doi, str):
                    match = DOI_REGEX.search(doi)
                    if match:
                        clean_doi = match.group(1)
                        logger.debug(f"Found DOI via PyPDF2 metadata for {pdf_filename}: {clean_doi}")
                        return clean_doi
    except FileNotFoundError:
        logger.error(f"File not found for DOI extraction: {pdf_path}")
        return None # Cannot proceed if file doesn't exist
    except PyPDF2.errors.PdfReadError as pe:
        logger.warning(f"PyPDF2 could not read {pdf_filename} for metadata (potentially corrupted): {pe}")
    except Exception as e:
        logger.warning(f"PyPDF2 failed to read metadata for {pdf_filename}: {e}", exc_info=True)

    # 2. Try Docling Metadata (Speculative)
    # Placeholder - Adjust if docling provides usable metadata
    # if conversion_result and hasattr(conversion_result, 'document') and hasattr(conversion_result.document, 'meta'):
    #     try:
    #         docling_meta = conversion_result.document.meta
    #         if isinstance(docling_meta, dict) and docling_meta.get('doi'):
    #             # ... (add regex validation/cleaning here too)
    #     except Exception as e:
    #         logger.warning(f"Error accessing docling metadata for {pdf_filename}: {e}")

    # 3. Try Regex on Text (using conversion_result if available)
    text_to_search = None
    if conversion_result and hasattr(conversion_result, 'document'):
        try:
            # Attempt to get plain text export
            if hasattr(conversion_result.document, 'export_to_plain_text'):
                text_to_search = conversion_result.document.export_to_plain_text()
                logger.debug(f"Using docling plain text export for regex search in {pdf_filename}")
            elif hasattr(conversion_result.document, 'text'):
                 text_to_search = conversion_result.document.text # Fallback
                 logger.debug(f"Using docling document text attribute for regex search in {pdf_filename}")
        except Exception as e:
            logger.warning(f"Error getting text from docling result for regex search in {pdf_filename}: {e}")

    # If docling text failed, try PyPDF2 text extraction as fallback
    if not text_to_search:
        logger.debug(f"Docling text extraction failed or not available for {pdf_filename}, trying PyPDF2.")
        try:
            text_parts = []
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f, strict=False)
                num_pages_to_check = min(5, len(reader.pages)) # Check first 5 pages
                logger.debug(f"Checking first {num_pages_to_check} pages with PyPDF2 for {pdf_filename}")
                for i in range(num_pages_to_check):
                    try:
                        page = reader.pages[i]
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    except Exception as page_e:
                         logger.warning(f"PyPDF2 failed to extract text from page {i+1} of {pdf_filename}: {page_e}")
            if text_parts:
                text_to_search = "\n".join(text_parts)
        except PyPDF2.errors.PdfReadError as pe:
             logger.warning(f"PyPDF2 could not read {pdf_filename} for text extraction (potentially corrupted): {pe}")
        except Exception as e:
             logger.warning(f"PyPDF2 failed to extract text for {pdf_filename}: {e}", exc_info=True)

    # Perform regex search if text was obtained
    if text_to_search:
        logger.debug(f"Performing regex search on extracted text for {pdf_filename}...")
        match = DOI_REGEX.search(text_to_search)
        if match:
            doi = match.group(1) # Group 1 contains the DOI without word boundaries
            logger.debug(f"Found DOI via regex in {pdf_filename}: {doi}")
            return doi.strip()
        else:
             logger.debug(f"DOI pattern not found via regex in {pdf_filename}.")
    else:
        logger.warning(f"Could not extract any text for regex search from {pdf_filename}.")

    logger.debug(f"DOI extraction fully failed for {pdf_filename}.")
    return None

def process_single_pdf(pdf_path: str, output_dir: str, converter: DocumentConverter, chunker: HybridChunker) -> bool:
    """Processes a single PDF file: converts, extracts DOI, chunks, and saves JSON."""
    pdf_filename = os.path.basename(pdf_path)
    json_filename = os.path.splitext(pdf_filename)[0] + '.json'
    output_json_path = os.path.join(output_dir, json_filename)

    # Skip if JSON already exists (add --overwrite flag later if needed) - REMOVED
    # The check in main() now handles the --overwrite logic.
    # if os.path.exists(output_json_path):
    #     logger.info(f"Skipping {pdf_filename} as output JSON already exists: {output_json_path}")
    #     return True # Consider existing file a success for the summary

    logger.info(f"--- Processing {pdf_filename} ---")

    conversion_result = None # Define outside try block for DOI extraction
    extracted_doi = None
    # chunks = [] # Will use filtered_chunks instead
    try:
        # 1. Extract DOI (Attempt PyPDF2 first, before potentially slow conversion)
        logger.debug(f"Attempting DOI extraction (pre-conversion) for {pdf_filename}...")
        extracted_doi = extract_doi(pdf_path) # Try without conversion result first
        if extracted_doi:
             logger.info(f"DOI extracted (pre-conversion) for {pdf_filename}: {extracted_doi}")

        # 2. Convert PDF using Docling
        logger.debug(f"Converting {pdf_filename}...")
        conversion_result = converter.convert(pdf_path)
        if not conversion_result or not conversion_result.document:
            raise ValueError("Docling conversion failed or returned empty result.")
        logger.debug(f"Conversion successful for {pdf_filename}.")

        # 3. Extract DOI again (using text from conversion if not found before)
        if not extracted_doi:
            logger.debug(f"Attempting DOI extraction (post-conversion) for {pdf_filename}...")
            extracted_doi = extract_doi(pdf_path, conversion_result)

        if extracted_doi:
            doi_value = extracted_doi
            # Log only if found post-conversion (already logged if pre-conversion)
            if doi_value != DOI_MISSING_PLACEHOLDER and not logger.isEnabledFor(logging.INFO): # Avoid double logging
                 logger.info(f"DOI extracted (post-conversion) for {pdf_filename}: {doi_value}")
        else:
            doi_value = DOI_MISSING_PLACEHOLDER
            logger.warning(f"DOI not found for {pdf_filename}. Using placeholder.")

        # 4. Chunk Document and Filter
        logger.debug(f"Chunking and filtering {pdf_filename}...")
        chunk_iter = chunker.chunk(conversion_result.document)
        filtered_chunks = [] # Store filtered chunks here
        for i, chunk in enumerate(chunk_iter):
            chunk_text = chunk.text.strip() if chunk.text else ""
            if not chunk_text:
                logger.debug(f"Skipping empty chunk {i+1} for {pdf_filename}")
                continue

            keep_chunk = True
            filter_reason = ""

            # 1. Check contextualized header
            try:
                # Replace deprecated serialize with contextualize
                contextualized_text = chunker.contextualize(chunk=chunk)
                # Check the first line (or ~50 chars) for headers
                first_line = contextualized_text.split('\n', 1)[0].lower().strip()
                # More robust check: check start of first line OR start of entire text
                context_lower_stripped = contextualized_text.lower().strip()
                if any(first_line.startswith(header) for header in NON_MAIN_HEADERS) or \
                   any(context_lower_stripped.startswith(header) for header in NON_MAIN_HEADERS):
                     keep_chunk = False
                     # Find the specific header that matched for logging
                     matched_header = next((h for h in NON_MAIN_HEADERS if first_line.startswith(h) or context_lower_stripped.startswith(h)), "unknown")
                     filter_reason = f"Header match ({matched_header})"

            except Exception as context_err:
                logger.warning(f"Could not get contextualized text for chunk {i+1} in {pdf_filename}: {context_err}")
                # Conservative approach: Keep chunk if contextualization fails

            # 2. If not filtered by header, check text patterns
            if keep_chunk:
                for pattern in NON_MAIN_PATTERNS:
                    if pattern.search(chunk_text):
                        keep_chunk = False
                        filter_reason = f"Pattern match ({pattern.pattern})"
                        break # Stop checking patterns once a match is found

            # 3. Append chunk if it's considered main content
            if keep_chunk:
                chunk_data = {
                    "content": chunk_text,
                    "source": doi_value,
                    "file_path": ""
                }
                filtered_chunks.append(chunk_data)
            else:
                logger.debug(f"Filtering chunk {i+1} from {pdf_filename}. Reason: {filter_reason}. Content preview: {chunk_text[:100]}...")

        # Use filtered_chunks instead of original chunks list
        if not filtered_chunks:
            logger.warning(f"No valid content chunks remaining after filtering for {pdf_filename}. Output file will be empty.")
        else:
             logger.debug(f"Generated {len(filtered_chunks)} chunks (after filtering) for {pdf_filename}.")

        # 5. Save to JSON (use filtered_chunks)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_chunks, f, ensure_ascii=False, indent=4) # Save filtered_chunks

        # Update log message to reflect filtered count
        logger.info(f"Successfully processed {pdf_filename} -> {json_filename} ({len(filtered_chunks)} chunks saved after filtering, DOI Found: {extracted_doi is not None})")
        return True

    except FileNotFoundError:
         logger.error(f"File not found during processing: {pdf_path}")
         return False
    except PyPDF2.errors.PdfReadError as pe:
        logger.error(f"PyPDF2 failed to read {pdf_filename}, cannot process: {pe}")
        return False
    except Exception as e:
        logger.error(f"Failed to process {pdf_filename}: {e}", exc_info=True)
        # Clean up potentially incomplete JSON file
        if os.path.exists(output_json_path):
            try:
                # Check if file is empty or only contains `[]` before removing
                with open(output_json_path, 'r') as f_check:
                    content = f_check.read().strip()
                    if not content or content == '[]':
                         os.remove(output_json_path)
                         logger.warning(f"Removed empty/incomplete JSON: {output_json_path}")
            except OSError as remove_err:
                logger.error(f"Could not remove potentially incomplete JSON {output_json_path}: {remove_err}")
            except Exception as check_err:
                 logger.error(f"Error checking/removing incomplete JSON {output_json_path}: {check_err}")
        return False

# --- Main Execution ---
def main(args):
    """Main processing loop."""
    logger.info("--- Starting PDF Chunk Processing ---")
    # logger.info(f"PDF Input Directory: {args.pdf_dir}") # Remove old log
    logger.info(f"JSON Output Directory: {args.chunks_dir}")
    logger.info(f"Max Chunk Tokens: {MAX_CHUNK_TOKENS}")
    # logger.info(f"Tokenizer Encoding: {TOKENIZER_ENCODING}") # Not relevant when using default

    # Ensure output directories exist
    try:
        os.makedirs(args.chunks_dir, exist_ok=True)
        os.makedirs(DOI_DIR, exist_ok=True) # For the mapping file later
    except OSError as e:
        logger.critical(f"Failed to create output directories: {e}. Exiting.")
        return

    chunker = get_chunker()
    if not chunker:
        logger.critical("Failed to initialize chunker. Exiting.")
        return

    try:
        converter = DocumentConverter()
        logger.info("Docling DocumentConverter initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize DocumentConverter: {e}. Exiting.", exc_info=True)
        return

    # --- Determine input files based on input_path ---
    pdf_files = []
    pdf_input_dir = None
    input_path = args.input_path

    if os.path.isdir(input_path):
        pdf_input_dir = input_path
        logger.info(f"Processing PDF files in directory: {pdf_input_dir}")
        try:
            pdf_files = [f for f in os.listdir(pdf_input_dir) if f.lower().endswith('.pdf')]
            logger.info(f"Found {len(pdf_files)} PDF files.")
        except FileNotFoundError:
            logger.critical(f"Input directory not found: {pdf_input_dir}. Exiting.")
            return
        except Exception as e:
            logger.critical(f"Error listing PDF files in {pdf_input_dir}: {e}. Exiting.")
            return
    elif os.path.isfile(input_path):
        if input_path.lower().endswith('.pdf'):
            pdf_input_dir = os.path.dirname(input_path)
            # Ensure pdf_input_dir is not empty if the file is in the current directory
            if not pdf_input_dir:
                 pdf_input_dir = '.'
            pdf_files = [os.path.basename(input_path)]
            logger.info(f"Processing single PDF file: {input_path}")
        else:
            logger.critical(f"Input path is a file but not a PDF: {input_path}. Exiting.")
            return
    else:
         logger.critical(f"Input path is not a valid file or directory: {input_path}. Exiting.")
         return

    if not pdf_files:
         logger.info("No PDF files found to process. Exiting.")
         return
    # --- End input file determination ---

    success_count = 0
    fail_count = 0
    skipped_count = 0

    for pdf_file in pdf_files:
        # Use the determined pdf_input_dir here
        pdf_path = os.path.join(pdf_input_dir, pdf_file) # Make sure this uses pdf_input_dir
        json_filename = os.path.splitext(pdf_file)[0] + '.json'
        output_json_path = os.path.join(args.chunks_dir, json_filename)

        # Check if file is empty or invalid before processing
        try:
            if os.path.getsize(pdf_path) == 0:
                logger.warning(f"Skipping empty file: {pdf_file}")
                fail_count += 1 # Count as failure if empty
                continue
        except FileNotFoundError:
             logger.error(f"File disappeared during processing? {pdf_path}")
             fail_count += 1
             continue
        except Exception as e:
             logger.error(f"Error checking file size for {pdf_path}: {e}")
             fail_count += 1
             continue

        # Skip if JSON already exists and overwrite is False
        if not args.overwrite and os.path.exists(output_json_path):
            logger.info(f"Skipping {pdf_file} as output JSON already exists: {output_json_path}")
            skipped_count += 1
            continue

        processed_ok = process_single_pdf(pdf_path, args.chunks_dir, converter, chunker)
        if processed_ok:
            # Check if it was skipped due to already existing
             if not args.overwrite and os.path.exists(output_json_path):
                 pass # Already counted as skipped
             else:
                 success_count += 1
        else:
            fail_count += 1

    # Count missing DOI files by reading the log
    missing_doi_count = 0
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
            # More specific count
            missing_doi_count = log_content.count("DOI not found for")
            # Could also parse logs for better accuracy if needed
    except FileNotFoundError:
        logger.info("Log file not found for final summary (or no missing DOIs logged). Missing DOI count will be 0.")
    except Exception as e:
        logger.warning(f"Error reading log file for summary: {e}")

    logger.info("--- PDF Chunk Processing Finished ---")
    logger.info(f"Total PDF files found: {len(pdf_files)}")
    logger.info(f"Successfully processed/created: {success_count}")
    logger.info(f"Skipped (already exist): {skipped_count}")
    logger.info(f"Failed to process: {fail_count}")
    logger.info(f"Files logged with missing DOI (check log): {missing_doi_count}")
    logger.info(f"Logs saved to: {LOG_FILE}")
    logger.info(f"JSON chunks saved to: {args.chunks_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process PDF files, chunk them, and extract DOIs.")
    # parser.add_argument("--pdf-dir", default=PDF_DIR, help=f"Directory containing input PDF files (default: {PDF_DIR})") # Removed
    parser.add_argument("--input-path", required=True, help="Path to the input PDF file or directory containing PDF files.") # Added
    parser.add_argument("--chunks-dir", default=CHUNKS_DIR, help=f"Directory to save output JSON chunk files (default: {CHUNKS_DIR})")
    parser.add_argument("--overwrite", action='store_true', help="Overwrite existing JSON chunk files.")
    args = parser.parse_args()

    main(args) 
