FROM python:3.9-alpine

RUN adduser -D poller
WORKDIR /home/poller/

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY tg_api ./app_poller/tg_api
COPY poller.py rmq_sender.py run_poller.py ./app_poller/
COPY main.py .
RUN chown -R poller:poller ./

USER poller
CMD ["python3", "main.py"]




