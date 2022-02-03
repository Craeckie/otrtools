#!/bin/sh
sudo systemctl start rabbitmq.service
# sudo systemctl status rabbitmq.service
celery -A otrtools --broker amqp://user:FzWcvA_rCCgq-V_hDXoIMM4ySYpecuz@localhost:5672/vhost worker -l info

