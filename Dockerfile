
FROM python:3.7-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app

ENV DEBUG "True"
ENV PYTHONUNBUFFERED '1'
ENV LCA_APP_ENV 'development'  
ENV GOOGLE_APPLICATION_CREDENTIALS './config/gcp/genuine-wording-key.json'
ENV AI_SERVICE_URL 'http://34.93.6.90'

ENV PORT 8080 

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python3", "app-run.py"]
