FROM python:3.12
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN python -m pip install -r requirements.txt
CMD ["uvicorn","main:app", "--host", "0.0.0.0","--port", "80"]