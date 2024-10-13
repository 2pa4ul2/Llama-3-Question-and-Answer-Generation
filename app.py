from flask import Flask, request, jsonify, render_template
from langchain_community.llms import Ollama
import os, pdfplumber


app = Flask(__name__)

#import model
llm = Ollama(model="llama3")

#Variables
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No file selected for uploading"}), 400

        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            prompt = """
                    Generate multiple-choice questions from the following text. For each question, provide four options (a, b, c, d) and specify the correct answer at the end in the following format:

                    1. Question text here?
                    a) Option A
                    b) Option B
                    c) Option C
                    d) Option D

                    Answer: [correct answer letter]

                    The questions should be clear, concise, and relevant to the text. Here is the text:
                    """
            text = extract_pdf_text(file_path)
            formatted_prompt = text+prompt
            if text:
                result = llm.invoke(formatted_prompt)
                return jsonify({"message": "File successfully uploaded", "text": text, "result": result})
            else:
                return jsonify({"message": "Error extracting text from the PDF file"}), 400


if __name__ == '__main__':
    app.run(debug=True)