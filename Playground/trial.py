from flask import Flask, request, jsonify, render_template
from langchain_community.llms import Ollama
import os, pdfplumber


app = Flask(__name__)

#import model
llm = Ollama(model="llama3")

#Variables
UPLOAD_FOLDER = 'Playground/static/uploads'
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
            text = extract_pdf_text(file_path)
            if text:
                return render_template('upload.html', text=text)
            else:
                return jsonify({"message": "Error extracting text from the PDF file"}), 400

@app.route('/generate', methods=['POST'])
def generate_questions():

    text = request.form.get('text')
    if not text:
        return jsonify({"message": "No text provided. Please upload a file first."}), 400
    # Get the form data
    number_of_questions = request.form.get('number')  # The number of questions entered
    question_type = request.form.get('type')  # The selected question type

    # Apply logic based on the selected question type
    if question_type == 'MCQ':
        # return f"Generating {number_of_questions} Multiple Choice Questions"
        prompt = f"""
                Generate {number_of_questions} multiple-choice questions from the following text. For each question, provide four options (a, b, c, d) and specify the correct answer at the end in the following format:

                    1. Question text here?
                    a) Option A
                    b) Option B
                    c) Option C
                    d) Option D

                    Answer: [correct answer letter]

                    The questions should be clear, concise, and relevant to the text. Here is the text:
                    """
        formatted_prompt = text+prompt
        result = llm.invoke(formatted_prompt)
        return render_template('generated.html', result=result)
    elif question_type == 'TOF':
        prompt = f"""
                Generate {number_of_questions} True or False Questions from the following text. For each question, specify the correct answer at the end in the following format:

                    1. Question text here?
                    a) True
                    b) False

                    Answer: [correct answer letter]

                    The questions should be clear, concise, and relevant to the text. Here is the text:
                    """
        formatted_prompt = text+prompt
        result = llm.invoke(formatted_prompt)
        return render_template('generated.html', result=result)
    elif question_type == 'IDN':
        prompt = f"""
                Generate {number_of_questions} Identification Questions from the following text. For each question, specify the correct answer at the end in the following format:

                    1. Question text here?

                    Answer: [correct answer]

                    The questions should be clear, concise, and relevant to the text. Here is the text:
                    """
        formatted_prompt = text+prompt
        result = llm.invoke(formatted_prompt)
        return render_template('generated.html', result=result)
    else:
        return "Invalid selection"

if __name__ == '__main__':
    app.run(debug=True)

    # prompt = """
    #                 Generate multiple-choice questions from the following text. For each question, provide four options (a, b, c, d) and specify the correct answer at the end in the following format:

    #                 1. Question text here?
    #                 a) Option A
    #                 b) Option B
    #                 c) Option C
    #                 d) Option D

    #                 Answer: [correct answer letter]

    #                 The questions should be clear, concise, and relevant to the text. Here is the text:
    #                 """
    #         text = extract_pdf_text(file_path)
    #         formatted_prompt = text+prompt