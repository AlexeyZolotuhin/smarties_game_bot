FROM python:3.10-alpine

RUN adduser -D worker
WORKDIR /home/worker

COPY wait-rabbit.py .

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY alembic alembic
COPY alembic.ini config.yml main.py questions_for_quiz ./

USER worker
CMD ["python", "-m", "alembic", "upgrade", "head"]
#CMD ["python", "main.py"]

