import os
import sys
import re
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import tempfile

# Add the current directory to the Python path so we can import requirements_analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requirements_analyzer

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # In production, use a secure secret key

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def markdown_table_to_html(markdown_table):
    """Convert a markdown table to HTML table."""
    lines = markdown_table.strip().split('\n')
    
    if len(lines) < 3:
        return markdown_table  # Not enough lines for a table
    
    # Extract headers (first line)
    headers = [header.strip() for header in lines[0].split('|') if header.strip()]
    
    # Skip the separator line (second line)
    
    # Extract rows
    rows = []
    for line in lines[2:]:  # Start from third line
        if line.strip():
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            rows.append(cells)
    
    # Generate HTML
    html = '<div class="table-responsive"><table class="table table-striped table-bordered">\n'
    
    # Add headers
    html += '  <thead class="table-dark">\n    <tr>\n'
    for header in headers:
        html += f'      <th>{header}</th>\n'
    html += '    </tr>\n  </thead>\n'
    
    # Add body
    html += '  <tbody>\n'
    for row in rows:
        html += '    <tr>\n'
        for cell in row:
            # Handle line breaks in cells
            cell_content = cell.replace('<br>', '<br/>').replace('\\n', '<br/>')
            html += f'      <td>{cell_content}</td>\n'
        html += '    </tr>\n'
    html += '  </tbody>\n'
    
    html += '</table></div>'
    
    return html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    api_key = request.form.get('api_key', '').strip()
    use_sample = 'use_sample' in request.form
    
    # Use a temporary file to store uploaded content
    temp_file_path = None
    
    try:
        if use_sample:
            # Use the sample requirements file
            requirements_file_path = 'sample_requirements.txt'
        else:
            # Check if a file was uploaded
            if 'requirements_file' not in request.files:
                flash('No file selected')
                return redirect(request.url)
            
            file = request.files['requirements_file']
            
            # If user does not select file, use sample
            if file.filename == '':
                requirements_file_path = 'sample_requirements.txt'
            elif file and allowed_file(file.filename):
                # Save the uploaded file to a temporary location
                filename = secure_filename(file.filename)
                temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(temp_file_path)
                requirements_file_path = temp_file_path
            else:
                flash('Invalid file type. Please upload a .txt file.')
                return redirect(request.url)
        
        # Read requirements
        requirements_text = requirements_analyzer.read_requirements_file(requirements_file_path)
        
        # Use provided API key or default
        original_api_key = requirements_analyzer.API_KEY
        if api_key:
            requirements_analyzer.API_KEY = api_key
        
        try:
            # Generate summary
            summary = requirements_analyzer.summarize_requirements(requirements_text)
            
            # Generate test cases
            test_cases = requirements_analyzer.generate_test_cases(requirements_text)
            
            # Save results
            output_file = "requirements_analysis.md"
            requirements_analyzer.save_results_to_file(summary, test_cases, output_file)
            
            # Read the results to display in the template
            with open(output_file, 'r', encoding='utf-8') as f:
                results_content = f.read()
            
            # Extract and convert test cases table to HTML
            test_cases_html = ""
            # Find the table in the test cases markdown
            table_match = re.search(r'\|.*\|(?:\n\|.*\|)+', test_cases)
            if table_match:
                test_cases_html = markdown_table_to_html(table_match.group(0))
            
            return render_template('results.html', 
                                 summary=summary, 
                                 test_cases=test_cases,
                                 test_cases_html=test_cases_html,
                                 results_content=results_content)
        finally:
            # Restore original API key
            requirements_analyzer.API_KEY = original_api_key
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))
    finally:
        # Clean up temporary file if it was created
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.route('/download')
def download():
    return render_template('download.html')

if __name__ == '__main__':
    app.run(debug=True)
