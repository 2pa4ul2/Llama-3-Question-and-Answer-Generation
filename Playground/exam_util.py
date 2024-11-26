import os
from PIL import Image
from pdf2image import convert_from_path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.llms import Ollama


def exam_convert_file_to_thumbnail(file_path, thumbnail_path, start_page=0, end_page=1, size=(256, 256)):
    # Convert PDF to a list of images (one per page)
    images = convert_from_path(file_path, dpi=180)

    # in case the pages are less than 10 (first set of pages to load)
    end_page = min(end_page, len(images)) 
    if end_page < start_page:
        print("No pages to convert.")
        return []
    # pages should be zero based
    # last page excluded 

    for count, page in enumerate(images[start_page:end_page], start=start_page):
        print(f"creating thumbnail of page: {count + 1}")
        page.thumbnail(size)
        thumbnail_file = os.path.join(thumbnail_path, f'thumbnail_{count}.jpg')
        page.save(thumbnail_file, 'JPEG')

    # Return the list of generated thumbnails
    return [f'thumbnail_{i}.jpg' for i in range(start_page, end_page)]


def exam_parse_page_ranges(pages):
    page_list = []
    for part in pages.split(','):
        part = part.strip() 
        if '-' in part:
            # Handle range, e.g., "2-6"
            start, end = map(int, part.split('-'))
            page_list.extend(range(start, end + 1))  # Add each page in the range
        else:
            # Handle single page, e.g., "5"
            page_list.append(int(part))
    
    return page_list



def exam_extract_text(file_path, pages):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()   

    extracted_text = ""
    for page_num in pages:
        if page_num <= len(docs):
            extracted_text += docs[page_num-1].page_content

    return extracted_text



def exam_generate_questions(questions, text):
    llm = Ollama(model="llama3.2")
    all_generated_questions = []
    
    # Prompts for each type of question
    question_prompts = {
        'MCQ': """
            Generate {number_of_questions} multiple-choice questions based on the provided text. Each question should include four options (a, b, c, d), with the correct answer specified at the end. Ensure the questions focus on "WH" questions (e.g., who, what, when, where, why, how) and avoid overly simplistic phrasing. Follow this format:

            Question: Write the question here, ensuring it is clear, specific, and not too common.
            a) Option A
            b) Option B
            c) Option C
            d) Option D

            Answer: [Correct answer letter, e.g., "a"] (Provide 1-2 words max.)

             NOTE:(Do not add unnecessary text like this: 
                Here are two true or false questions based on the text:
                Let me know if you need anything else!)
            """,

        'TOF': """
            Generate {number_of_questions} true or false questions based on the provided text. Each question should be straightforward, concise, and clearly related to the text. Specify the correct answer using the format below:

            Question: Write the true or false statement here.
            a) True
            b) False

            Answer: [Correct answer letter, e.g., "a"] (1-2 words max.)
            NOTE:(Do not add unnecessary text like this: 
                Here are two true or false questions based on the text:
                Let me know if you need anything else!)
            """,

        'IDN': """
            Generate {number_of_questions} identification questions based on the provided text. Each question should prompt the identification of a specific term, concept, or key detail. Specify the correct answer clearly at the end. Use this format:

            Question: Write the identification question here, ensuring clarity and relevance.

            Answer: [Correct answer] (not too long answer, Limit to 1-2 words.)
             NOTE:(Do not add unnecessary text like this: 
                Here are two true or false questions based on the text:
                Let me know if you need anything else!)
            """
    }

    # Loop through each selected question type and corresponding number of questions
    for question in questions:
        question_type = question.get('type')
        question_type = exam_abbreviate(question_type)

        num_questions = question.get('quantity')
        print(f"Generating {num_questions} {question_type} questions...")

        # Get the corresponding prompt for the current question type
        prompt_template = question_prompts.get(question_type)
        if prompt_template:
            # Format the prompt with the number of questions
            prompt = prompt_template.format(number_of_questions=num_questions)

            # Combine the text with the prompt
            formatted_prompt = text + prompt

            # Invoke the LLM (LangChain model) to generate questions
            result = llm.invoke(formatted_prompt, temperature=0.8, max_tokens=100)

            # Split the generated result into individual questions and answers
            question_list = parse_questions_and_answers(result)

            # Append the result to the list
            all_generated_questions.append({
                'type': question_type,
                'questions': question_list
            })

    return all_generated_questions

def parse_questions_and_answers(result):
    # This function processes the result and splits questions, options, and answers
    questions_and_answers = []
    lines = result.split('\n')

    current_question = ""
    options = {}
    current_answer = ""

    for line in lines:
        if line.startswith("Question:"):
            # New question starts
            if current_question:
                questions_and_answers.append({
                    'question': current_question.strip(),
                    'options': options,  # Add options
                    'answer': current_answer.strip()
                })
            current_question = line.replace("Question:", "").strip()
            options = {}  # Reset options for the new question
            current_answer = ""  # Reset answer for the new question
        elif line.startswith("a)") or line.startswith("b)") or line.startswith("c)") or line.startswith("d)"):
            # Capture options a), b), c), d)
            option_letter = line[0]  # a, b, c, d
            option_text = line[3:].strip()  # Extract the option text
            options[option_letter] = option_text  # Save it as part of the options dictionary
        elif line.startswith("Answer:"):
            current_answer = line.replace("Answer:", "").strip()

    # Add the last question
    if current_question:
        questions_and_answers.append({
            'question': current_question.strip(),
            'options': options,  # Add options
            'answer': current_answer.strip()
        })

    return questions_and_answers



def exam_abbreviate(q_type):
    return {'identification': 'IDN', 'multiple_choice': 'MCQ', 'true_or_false': 'TOF'}.get(q_type.lower(), 'UNKNOWN')




