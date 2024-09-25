from fastapi import FastAPI, File, UploadFile, Request
import google.generativeai as genai
from io import BytesIO
import json
import fitz
import asyncio

genai.configure(api_key="AIzaSyBw6MWF4aJnxBUgbJoEVxIfUYsCQBjmCwg")

generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

app = FastAPI()
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

@app.get("/")
async def home():
    return {"data": "home page"}


@app.post("/create_paper")
async def load_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pdf_document = fitz.open(stream=BytesIO(contents), filetype="pdf")

        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text()
        data = text

        # prompt = f"""persona - you are a question paper creater
        #              goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
        #              output format-{{["Question 1" : "Description", "option 1" : "Option 1 Description", "option 2" : "Option 2 Description","option 3" : "Option 3 Description","option 4" : "Option 4 Description", "Answer: "Right Answer key among A , B , C , D"] ...}}
        #              context - {data}"""

        prompt = f"""   persona - you are a question paper creater 
                        goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
                        instructions - there can be mathematical , hindi , english questions output values in human readable format . Focus of option orders and accuracy . Use decimal numbers system and dont use Odia system.
                        output format- {{
              [
                  {{
                      "question": "description of the question",
                      "options": [
                          {{
                              "value": "description of option 1 in human readable format",
                              "optionId": 1,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 2 in human readable format",
                              "optionId": 2,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 3 in human readable format",
                              "optionId": 3,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 4 in human readable format",
                              "optionId": 4,
                              "selected": always false,
                              "optionType": "normal"
                          }}
                      ],
                      "answer": "1",
                      "solution":"description of option 1 in human readable format"
                  }}, ...] }}

                  context - {data}"""

        convo = model.start_chat()
        await asyncio.to_thread(convo.send_message, prompt)

        try:
            return {"data": json.loads(convo.last.text)}
        except Exception as e:
            print("error type : " ,e)
            return {"data": ""}

    except Exception as e:
        print(e)
        return {"data": e}

@app.post("/generate_paper")
async def generate_paper(request:Request):
    try:
        config = await request.json()

        prompt = f"""
        persona - You are an expert question paper creator.
        Goal - Your job is to create an MCQ test for students based on the provided configuration . Output a JSON with given schema with questions, options, and correct answers.
        Instructions - There can be mathematical, Hindi, and English questions. Output values in human-readable format. Focus on accuracy.

        Configuration:
        Class: {config['class']}
        Subject: {config['subject']}
        Topic: {config['topic']}
        Difficulty: {config['difficulty']}
        Number of questions: {config['num_questions']}
        Language: {config['language']}

        Additional instructions:
        1. Ensure questions are age-appropriate for the specified class.
        2. Maintain the specified difficulty level throughout the paper.
        3. Include a mix of conceptual and application-based questions.
        4. For language questions, focus on grammar, vocabulary, and comprehension as appropriate.

        output format:
        {{
            "paper_details": {{
                "class": "{config['class']}",
                "subject": "{config['subject']}",
                "topic": "{config['topic']}",
                "difficulty": "{config['difficulty']}",
                "num_questions": {config['num_questions']},
                "language": "{config['language']}"
            }},
            "questions": [
                {{
                    "question_id": 1,
                    "question_text": "Description of the question",
                    "question_type": "mcq",
                    "options": [
                        {{
                            "value": "Description of option 1 in human-readable format",
                            "optionId": 1,
                            "selected": false,
                            "optionType": "normal"
                        }},
                        {{
                            "value": "Description of option 2 in human-readable format",
                            "optionId": 2,
                            "selected": false,
                            "optionType": "normal"
                        }},
                        {{
                            "value": "Description of option 3 in human-readable format",
                            "optionId": 3,
                            "selected": false,
                            "optionType": "normal"
                        }},
                        {{
                            "value": "Description of option 4 in human-readable format",
                            "optionId": 4,
                            "selected": false,
                            "optionType": "normal"
                        }}
                    ],
                    "correct_answer": _ ,
                    "explanation": "Detailed explanation of the correct answer"
                }},
                ...
            ]
        }}
        """

        convo = model.start_chat()
        response = await asyncio.to_thread(convo.send_message, prompt)

        try:
            return {"data": json.loads(response.text)}
        except Exception as e:
            return {"error": f"An unexpected error occurred while generating {e}" , "data" : {}}

    except Exception as e:
        return {"error": f"An unexpected error occurred while generating the paper {e}" , "data" : {}}


# import google.generativeai as genai
# from io import BytesIO
# import json
# import fitz
# import os
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from typing import List
# from docx import Document
# import pandas as pd

# genai.configure(api_key="AIzaSyBw6MWF4aJnxBUgbJoEVxIfUYsCQBjmCwg")

# generation_config = {
#     "temperature": 0,
#     "top_p": 0.95,
#     "top_k": 0,
#     "max_output_tokens": 8192,
#     "response_mime_type": "application/json",
# }

# safety_settings = [
#     {
#         "category": "HARM_CATEGORY_HARASSMENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_HATE_SPEECH",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
#     {
#         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#     },
# ]

# app = FastAPI()
# model = genai.GenerativeModel(model_name="gemini-1.5-flash",
#                               generation_config=generation_config,
#                               safety_settings=safety_settings)

# @app.get("/")
# async def home():
#     return {"data": "home page"}


# @app.post("/create_paper")
# async def load_pdf(file: UploadFile = File(...)):
#     try:

#         contents = await file.read()
#         pdf_document = fitz.open(stream=BytesIO(contents), filetype="pdf")

#         text = ""
#         for page_num in range(len(pdf_document)):
#             page = pdf_document[page_num]
#             text += page.get_text()
#         data = text

#         #
#         # prompt = f"""persona - you are a question paper creater
#         #              goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
#         #              output format-{{["Question 1" : "Description", "option 1" : "Option 1 Description", "option 2" : "Option 2 Description","option 3" : "Option 3 Description","option 4" : "Option 4 Description", "Answer: "Right Answer key among A , B , C , D"] ...}}
#         #              context - {data}"""

#         prompt = f"""   persona - you are a question paper creater 
#                         goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
#                         instructions - there can be mathematical , hindi , english questions output values in human readable format . Focus of option orders and accuracy . Use decimal numbers system and dont use Odia system.
#                         output format- {{
#               [
#                   {{
#                       "question": "description of the question",
#                       "options": [
#                           {{
#                               "value": "description of option 1 in human readable format",
#                               "optionId": 1,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 2 in human readable format",
#                               "optionId": 2,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 3 in human readable format",
#                               "optionId": 3,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 4 in human readable format",
#                               "optionId": 4,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }}
#                       ],
#                       "answer": "1"
#                   }}, ...] }}

#                   context - {data}"""

#         convo = model.start_chat()
#         convo.send_message(prompt)

#         try:
#             return {"data": json.loads(convo.last.text)}
#         except Exception as e:
#             print("error type : " ,e)
#             return {"data": ""}

#     except Exception as e:
#         print(e)
#         return {"data": e}

# def extract_tables_from_word(file, image_dir='extracted_images'):
#     os.makedirs(image_dir, exist_ok=True)

#     doc = Document(file)
#     all_tables = []

#     for table_idx, table in enumerate(doc.tables):
#         data = []
#         for row_idx, row in enumerate(table.rows):
#             row_data = []
#             for cell_idx, cell in enumerate(row.cells):
#                 cell_text = cell.text.strip()
#                 images = []

#                 for drawing in cell._element.xpath('.//w:drawing'):
#                     image = drawing.xpath('.//a:blip/@r:embed')
#                     if image:
#                         image_id = image[0]
#                         image_part = doc.part.related_parts[image_id]

#                         image_filename = f"{table_idx}_{row_idx}_{cell_idx}_{image_part.partname.split('/')[-1]}"
#                         with open(os.path.join(image_dir, image_filename), 'wb') as img_file:
#                             img_file.write(image_part.blob)

#                         images.append(image_filename)

#                 for pict in cell._element.xpath('.//w:pict'):
#                     image = pict.xpath('.//v:imagedata/@r:id')
#                     if image:
#                         image_id = image[0]
#                         image_part = doc.part.related_parts[image_id]

#                         image_filename = f"{table_idx}_{row_idx}_{cell_idx}_{image_part.partname.split('/')[-1]}"
#                         with open(os.path.join(image_dir, image_filename), 'wb') as img_file:
#                             img_file.write(image_part.blob)

#                         images.append(image_filename)

#                 if images:
#                     cell_text += ' (Images: ' + ', '.join(images) + ')'

#                 row_data.append(cell_text)
#             data.append(row_data)

#         df = pd.DataFrame(data[1:], columns=data[0])
#         all_tables.append(df)

#     return all_tables

# class ExtractedTable(BaseModel):
#     table: List[List[str]]


# @app.post("/extract-tables", response_model=List[ExtractedTable])
# async def extract_tables(file: UploadFile = File(...)):
#     if not file.filename.endswith('.docx'):
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .docx file.")
    
#     try:
#         file_path = file.file.read()
#         tables = extract_tables_from_word(file_path)

#         response = [ExtractedTable(table=df.values.tolist()) for df in tables]
#         return JSONResponse(content=response)
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

