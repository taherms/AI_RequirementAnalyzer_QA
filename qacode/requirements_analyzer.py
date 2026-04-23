import requests
import json
import csv
import os
import time
from typing import Dict, List, Tuple

# OpenRouter API configuration
API_KEY = "<API_KEY>"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"

def read_requirements_file(file_path: str) -> str:
    """Read the requirements from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Requirements file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

def call_openrouter_api(prompt: str, model: str = None) -> str:
    """Call the OpenRouter API with a given prompt, with retry logic for rate limiting."""
    if model is None:
        model = DEFAULT_MODEL
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional requirements analyst and QA engineer."},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    # Retry logic for rate limiting
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=data)
            
            # If we get a 429 (rate limit), wait and retry
            if response.status_code == 429:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"API request failed after {max_retries} attempts: {str(e)}")
            else:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Request failed. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
        except KeyError:
            raise Exception("Unexpected API response format")
    
    raise Exception(f"API request failed after {max_retries} attempts")

def summarize_requirements(requirements_text: str) -> str:
    """Generate a summary of the requirements using OpenRouter API."""
    prompt = f"""
    Please provide a concise summary of the following software requirements:
    
    {requirements_text}
    
    Your summary should include:
    1. Main objectives
    2. Key features
    3. Target users
    4. Technical constraints (if any)
    """
    
    return call_openrouter_api(prompt)

def generate_test_cases(requirements_text: str) -> str:
    """Generate test cases in tabular format using OpenRouter API."""
    prompt = f"""
    Based on the following software requirements, please generate test cases in a tabular format:
    
    {requirements_text}
    
    The table should have the following columns:
    1. Test Case ID
    2. Description
    3. Pre-conditions
    4. Test Steps
    5. Expected Result
    6. Priority (High/Medium/Low)
    
    Please provide at least 5 test cases that cover the main functionality.
    Format the output as a markdown table.
    """
    
    return call_openrouter_api(prompt)

def save_results_to_file(summary: str, test_cases: str, output_file: str = "requirements_analysis.md"):
    """Save the summary and test cases to a markdown file."""
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write("# Requirements Analysis\n\n")
        file.write("## Summary\n\n")
        file.write(summary)
        file.write("\n\n## Test Cases\n\n")
        file.write(test_cases)
    
    print(f"Results saved to {output_file}")

def main():
    """Main function to run the requirements analyzer."""
    print("Requirements Analyzer using OpenRouter API")
    print("=" * 50)
    
    # Allow user to input their own API key
    user_api_key = input("Enter your OpenRouter API key (or press Enter to use the default): ").strip()
    global API_KEY
    if user_api_key:
        API_KEY = user_api_key
        print("Using your API key.")
    else:
        print("Using default API key (may be rate limited).")
    
    # Get the requirements file path from user
    requirements_file = input("Enter the path to the requirements text file (or press Enter for 'sample_requirements.txt'): ").strip()
    
    if not requirements_file:
        requirements_file = "sample_requirements.txt"
    
    try:
        # Read requirements
        print(f"\nReading requirements from {requirements_file}...")
        requirements_text = read_requirements_file(requirements_file)
        print("Requirements loaded successfully!")
        
        # Generate summary
        print("\nGenerating summary...")
        summary = summarize_requirements(requirements_text)
        print("Summary generated!")
        
        # Generate test cases
        print("\nGenerating test cases...")
        test_cases = generate_test_cases(requirements_text)
        print("Test cases generated!")
        
        # Save results
        save_results_to_file(summary, test_cases)
        
        # Display results
        print("\n" + "=" * 50)
        print("SUMMARY:")
        print("=" * 50)
        print(summary)
        
        print("\n" + "=" * 50)
        print("TEST CASES:")
        print("=" * 50)
        print(test_cases)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
