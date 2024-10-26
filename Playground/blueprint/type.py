from flask import Blueprint, render_template, session,request, jsonify, render_template, current_app
import os, pdfplumber

type = Blueprint('type', __name__)

# PDF Text Extraction Function
def extract_pdf_text(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@type.route('/type', methods=['POST'])
def type_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected for uploading"}), 400

        if file:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            text = extract_pdf_text(file_path)
            if text:
                return render_template('questions.html', text=text)
            else:
                return jsonify({"message": "Error extracting text from the PDF file"}), 400

