
FROM python:3.7-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python3", "app-run.py"]
