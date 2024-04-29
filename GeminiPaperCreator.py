from langchain_community.document_loaders import PyPDFLoader
from fastapi import FastAPI , Request , File, UploadFile
import google.generativeai as genai
import uuid
import os
import tempfile

genai.configure(api_key=str(os.environ['api_key']))

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
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

@app.post("/create_paper")
async def load_pdf(file: UploadFile = File(...)):
      try:
          print("in try block")
          with tempfile.NamedTemporaryFile(delete=True) as tmp:
              tmp.write(await file.read())
              print("temp data",temp)
              tmp_file_path = tmp.name
              loader = PyPDFLoader(tmp_file_path, extract_images=True)
              data = loader.load()
              print("daatata",data)

          model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

          prompt = f"""persona - you are a question paper creater 
                       goal - your job is to look into provided context and create mcq test for students with only exact data as provided also output json with question no. and right option.
                       context - {data}"""

          convo = model.start_chat()
          convo.send_message(prompt)

          return {"data" : convo.last.text}

      except Exception as e:
          print("in exception block")
          return {"data" : e}

