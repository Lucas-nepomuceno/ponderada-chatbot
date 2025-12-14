FROM python:3.12-bookworm

RUN mkdir -p /usr/src/chatbot
WORKDIR /usr/src/chatbot
COPY requirements.txt /usr/src/chatbot/
RUN \
    python3 -m pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt
COPY . .