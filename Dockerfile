# FROM python:3.11

# RUN mkdir -p /app/static/upload
# ADD . /app
# WORKDIR /app

# RUN apt update -y \
#     && apt install -y build-essential libpoppler-cpp-dev pkg-config python3-dev \
#     && pip install -r requirements.txt

# RUN pip install rapidocr-onnxruntime gunicorn

# # Assuming your FastAPI app is in a file named GeminiPaperCreator.py
# # and the FastAPI instance is named 'app'
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "GeminiPaperCreator:app", "--bind", "0.0.0.0:8080"]


# FROM python:3.11
FROM public.ecr.aws/docker/library/python:3.11-slim
ADD . /app
WORKDIR /app
RUN apt update -y \
    # && apt install -y build-essential libpoppler-cpp-dev pkg-config python3-dev \
    && pip install -r requirements.txt
# RUN pip install rapidocr-onnxruntime
CMD exec gunicorn GeminiPaperCreator:app --host 0.0.0.0 --port 8080
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "GeminiPaperCreator:app", "--bind", "0.0.0.0:8080"]




# FROM python:latest
# RUN mkdir /app
# ADD . /app
# WORKDIR /app
# RUN mkdir /app/static/upload
# RUN apt update -y
# RUN apt install build-essential libpoppler-cpp-dev pkg-config python3-dev -y
# RUN pip install -r requirements.txt
# #RUN pip install gevent
# #CMD exec gunicorn -b 0.0.0.0:8080 -w 4 app:app
# #CMD exec gunicorn -b 0.0.0.0:8080 --worker-class eventlet --workers 1 --timeout 0 --threads 8 app:app
# #CMD exec python app.py
# CMD exec uvicorn GeminiPaperCreator:app --host 0.0.0.0 --port 8080

