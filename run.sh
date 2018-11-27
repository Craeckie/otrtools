#!/bin/bash
sudo systemctl start rabbitmq.service
python3 manage.py runserver &
celery -A otrtools worker -l info --broker amqp://user:FzWcvA_rCCgq-V_hDXoIMM4ySYpecuz@localhost:5672/vhost
