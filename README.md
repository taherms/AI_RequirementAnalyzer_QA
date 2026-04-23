# Requirements Analyzer with OpenRouter API

This Python project analyzes software requirements from a text file, generates a summary, and creates test cases in tabular format using the OpenRouter API.

The project now includes both a command-line interface and a web-based user interface.

## Features

- Reads software requirements from a text file
- Generates a concise summary of the requirements
- Creates comprehensive test cases in tabular format
- Uses OpenRouter API for AI-powered analysis
- Handles rate limiting with automatic retries
- Outputs results in a markdown file

## Prerequisites

- Python 3.6 or higher
- An OpenRouter API key (optional but recommended)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your requirements in a text file (see `sample_requirements.txt` for an example)
2. Run the analyzer:
   ```
   python3 requirements_analyzer.py
   ```
3. When prompted, you can:
   - Enter your OpenRouter API key (or press Enter to use the default key which may be rate limited)
   - Enter the path to your requirements file (or press Enter to use the sample file)
4. The program will generate a summary and test cases, then save them to `requirements_analysis.md`

## Configuration

To use your own OpenRouter API key:
1. Sign up at [OpenRouter](https://openrouter.ai/) to get an API key
2. Either:
   - Enter your API key when prompted when running the script, or
   - Replace the `API_KEY` value in `requirements_analyzer.py` with your actual API key

## Output

The program generates a markdown file (`requirements_analysis.md`) with:
1. A summary of the requirements
2. Test cases in tabular format

## Customization

You can modify the prompts in the `summarize_requirements` and `generate_test_cases` functions to customize the output format or focus on specific aspects of the requirements.

## Web Interface

The project also includes a web-based user interface built with Flask. To use the web interface:

1. Run the web application:
   ```
   python3 app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the web interface to:
   - Enter your OpenRouter API key (optional)
   - Upload a requirements text file or use the sample file
   - Generate analysis results with summary and test cases
   - Download the results as a markdown file

The web interface provides a more user-friendly way to interact with the requirements analyzer, especially for users who prefer a graphical interface over command-line tools.
