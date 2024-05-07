FROM python:3.11
LABEL maintainer="tkacuk2291@gmail.com"
ENV PYTHONBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

#CMD ["python", "manage.py" , "runserver" , "0.0.0.0:8093"]
