
FROM python:3.10-slim-buster

RUN mkdir /app
ADD . /app
WORKDIR /app
ENV GOOGLE_APPLICATION_CREDENTIALS='store/genuine-wording-key.json'
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#EXPOSE 8000
CMD ["python3", "app.py"]

#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
#FROM alpine
#COPY apprun.sh 
#RUN apk --update add --no-cache g++
#RUN pip3 install numpy pandas 
#CMD ["/apprun.sh"]
#FROM python:3.10-alpine
#CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
#RUN pip install pandas