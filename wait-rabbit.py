#!/usr/local/bin/python
import pika

while True:
  rmq_params = pika.URLParameters("amqp://user_mq:pass_mq@tg-rabbitmq:5672/")
  try:
    pika.BlockingConnection(rmq_params)
  except:
    print("rabbit is not avalible")
    continue
  else:
    print("rabbit is avalible")
    break