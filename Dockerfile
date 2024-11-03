FROM python:3.10-slim
ENV BOT_TOKEN=""
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /app/logger/log
RUN mkdir /app/post_tmp
CMD ["python", "main.py"]