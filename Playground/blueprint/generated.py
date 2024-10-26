from flask import Blueprint, render_template, session
from flask import Flask, request, jsonify, render_template
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

generated = Blueprint('generated', __name__)

@generated.route('/generate', methods=['POST'])
def generate_questions_page():
    # Get the text and validate it
    text = request.form.get('text')
    if not text:
        return jsonify({"message": "No text provided. Please upload a file first."}), 400

    # Get all the selected question types and corresponding numbers
    question_types = request.form.getlist('type')
    question_numbers = request.form.getlist('number')

    # Dictionary to store all generated questions based on the type
    all_generated_questions = []

    # Prompts for each type of question
    question_prompts = {
        'MCQ': """
            Generate {number_of_questions} multiple-choice questions from the following text. 
            For each question, provide four options (a, b, c, d) and specify the correct answer 
            at the end in the following format:

                1. Question text here?
                a) Option A
                b) Option B
                c) Option C
                d) Option D

                Answer: [correct answer letter]

                The questions should be clear, concise, and relevant to the text. Here is the text:
            """,

        'TOF': """
            Generate {number_of_questions} True or False questions from the following text. 
            For each question, specify the correct answer at the end in the following format:

                1. Question text here?
                a) True
                b) False

                Answer: [correct answer letter]

                The questions should be clear, concise, and relevant to the text. Here is the text:
            """,

        'IDN': """
            Generate {number_of_questions} Identification Questions from the following text. 
            For each question, specify the correct answer at the end in the following format:

                1. Question text here?

                Answer: [correct answer]

                The questions should be clear, concise, and relevant to the text. Here is the text:
            """
    }

    # Loop through each selected question type and corresponding number of questions
    for question_type, num_questions in zip(question_types, question_numbers):
        num_questions = int(num_questions)  # Convert number of questions to integer

        # Get the corresponding prompt for the current question type
        prompt_template = question_prompts.get(question_type)
        if prompt_template:
            # Format the prompt with the number of questions
            prompt = prompt_template.format(number_of_questions=num_questions)

            # Combine the text with the prompt
            formatted_prompt = text + prompt

            # Invoke the LLM (LangChain model) to generate questions
            result = llm.invoke(formatted_prompt)

            # Append the result to the list
            all_generated_questions.append({
                'type': question_type,
                'questions': result
            })

    # Return the generated questions to the frontend
    return render_template('generated.html', generated_questions=all_generated_questions)