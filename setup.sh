#!/bin/sh
rabbitmqctl add_user user FzWcvA_rCCgq-V_hDXoIMM4ySYpecuz
rabbitmqctl add_vhost vhost
rabbitmqctl set_permissions user '.*' '.*' '.*'
