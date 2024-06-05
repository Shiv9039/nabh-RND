from langchain_community.document_loaders import PyPDFLoader
from fastapi import FastAPI, Request, File, UploadFile
import google.generativeai as genai
import uuid
import json
import os

genai.configure(api_key="AIzaSyBGB1mXdikSsTXoiIL8-VdhHpclMZ5yJuE")

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


@app.get("/")
async def home():
    return {"data": "home page"}


@app.post("/create_paper")
async def load_pdf(file: UploadFile = File(...)):
    try:

        filename = file.filename
        path = f"static/upload/{uuid.uuid4()}{filename}"

        with open(path, "wb") as buffer:
            buffer.write(await file.read())

        loader = PyPDFLoader(path, extract_images=False)
        data = loader.load()

        os.remove(path)

        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)
        #
        # prompt = f"""persona - you are a question paper creater
        #              goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
        #              output format-{{["Question 1" : "Description", "option 1" : "Option 1 Description", "option 2" : "Option 2 Description","option 3" : "Option 3 Description","option 4" : "Option 4 Description", "Answer: "Right Answer key among A , B , C , D"] ...}}
        #              context - {data}"""

        prompt = f"""persona - you are a question paper creater 
                        goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
                        output format- {{
              [
                  {{
                      "question": "description of the question",
                      "options": [
                          {{
                              "value": "description of option 1",
                              "optionId": 1,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 2",
                              "optionId": 2,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 3",
                              "optionId": 3,
                              "selected": always false,
                              "optionType": "normal"
                          }},
                          {{
                              "value": "description of option 4",
                              "optionId": 4,
                              "selected": always false,
                              "optionType": "normal"
                          }}
                      ],
                      "answer": "1"
                  }}, ...] }}

                  context - {data}"""

        convo = model.start_chat()
        convo.send_message(prompt)

        try:
            return {"data": json.loads(convo.last.text)}
        except Exception as e:
            print("error type : " ,e)
            return {"data": ""}

    except Exception as e:
        print(e)
        return {"data": e}





# from langchain_community.document_loaders import PyPDFLoader
# from fastapi import FastAPI , Request , File, UploadFile
# import google.generativeai as genai
# import uuid
# import os

# genai.configure(api_key=str(os.environ['api_key']))

# generation_config = {
#   "temperature": 1,
#   "top_p": 0.95,
#   "top_k": 0,
#   "max_output_tokens": 8192,
# }

# safety_settings = [
#   {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_HATE_SPEECH",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
# ]

# app = FastAPI()

# @app.get("/")
# async def home():
#     return {"data": "home page"}

# @app.post("/create_paper")
# async def load_pdf(file: UploadFile = File(...)):
#       try:

#           filename = file.filename
#           path = f"static/upload/{uuid.uuid4()}{filename}"

#           with open(path, "wb") as buffer:
#               buffer.write(await file.read())

#           loader = PyPDFLoader(path, extract_images=True)
#           data = loader.load()

#           os.remove(path)

#           model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
#                                         generation_config=generation_config,
#                                         safety_settings=safety_settings)
#           #
#           # prompt = f"""persona - you are a question paper creater
#           #              goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
#           #              output format-{{["Question 1" : "Description", "option 1" : "Option 1 Description", "option 2" : "Option 2 Description","option 3" : "Option 3 Description","option 4" : "Option 4 Description", "Answer: "Right Answer key among A , B , C , D"] ...}}
#           #              context - {data}"""

#           prompt = f"""persona - you are a question paper creater 
#                         goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
#                         output format- {{
#               [
#                   {{
#                       "question": "description of the question",
#                       "options": [
#                           {{
#                               "value": "description of option 1",
#                               "optionId": 1,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 2",
#                               "optionId": 2,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 3",
#                               "optionId": 3,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }},
#                           {{
#                               "value": "description of option 4",
#                               "optionId": 4,
#                               "selected": always false,
#                               "optionType": "normal"
#                           }}
#                       ],
#                       "answer": "1"
#                   }}, ...] }}
                  
#                   context - {data}"""

#           convo = model.start_chat()
#           convo.send_message(prompt)

#           return {"data" : convo.last.text}

#       except Exception as e:
#           print(e)
#           return {"data" : e}
