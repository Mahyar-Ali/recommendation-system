FROM python:3.10.6

WORKDIR /app


COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# install extra dependencies
RUN python install.py

EXPOSE 8080

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080","--timeout-keep-alive","300"]
