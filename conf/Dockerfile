FROM python:3.9-slim

WORKDIR /code

ENV CONTAINERIZED   1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install -y gcc python3-dev musl-dev netcat

RUN python3 -m pip install --upgrade pip

COPY *requirements.txt ./

RUN pip3 install -r prod-requirements.txt

COPY . .

ENTRYPOINT [ "/code/conf/entrypoint.sh" ]