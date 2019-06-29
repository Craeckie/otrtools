#!/bin/bash
sudo systemctl start rabbitmq.service
#python3 manage.py runserver &
celery -E -A otrtools worker -l info --broker amqp://my_user:ilgaOUGJpKi3hd_7EtUjlof9sp8yTrGeZqPZH_wTOYt2FVEOJs@localhost:5672/vhost
