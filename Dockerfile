FROM python:3.9-alpine
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "main.py"]