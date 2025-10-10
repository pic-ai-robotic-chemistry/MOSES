# MOSES

## Getting Started

### Prerequisites

-   Python 3.13
-   An API key of OpenAI.

### Installation

1.  **Clone the repository:**

    ```
    git clone https://github.com/pic-ai-robotic-chemistry/MOSES.git
    ```

2.  Install dependencies:

    (It is recommended to use a virtual environment)

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**

    -   Create a `.env` file.

    -   Add your API keys to the `.env` file:

        ```
        OPENAI_API_KEY="YOUR_API_KEY_HERE"
        ```

### Configuration

-   Review and adjust settings in `config/settings.yaml` to specify the desired LLM models, file paths, and other parameters.

## Usage

To run the question-answering workflow, you can use the test scripts as a starting point.

```bash
# Navigate to the test directory
cd test/question_answering

# Run the workflow test script
python workflow_test.py
```

You can modify `workflow_test.py` to load your own ontology and ask custom questions:

```python
# change the ontology
test_ontology_settings = OntologySettings(
            base_iri=test_base_iri,
            ontology_file_name="final.owl",  # Use the desired ontology file
            directory_path=ontology_dir,
            # closed_ontology_file_name="final-closed.owl" 
        )

# change the questions
total_qas = [...   #The question field is required.
```

## License

This project is licensed under the terms of the [LICENSE](https://www.google.com/search?q=LICENSE) file.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to discuss your ideas.