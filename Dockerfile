FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./main.py /app/

COPY ./machine.py /app/

COPY ./.env /app/

CMD ["python", "-u", "main.py"]