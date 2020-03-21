FROM python:slim

ENV wwwdir="/var/www" \
    REPO_DIR="/var/www/otrtools" \
    CPU_CORES="3" \
    LANG="en_US.utf8" \
    LC_ALL="en_US.UTF-8" \
    LC_LANG="en_US.UTF-8" \
    PYTHONIOENCODING="UTF-8" \
    REPO_DIR="/var/www/otrtools"

WORKDIR /root
ADD docker/ffmpeg-build.sh ./
RUN apt-get update>apt-get-update.log \
      && apt-get install --no-install-recommends -y  \
      libmcrypt-dev libcurl4-openssl-dev git  \
      build-essential libglib2.0-dev libssl-dev libcurl4-openssl-dev \
      libgirepository1.0-dev automake asciidoc libxml2-utils libtool \
      yasm bzip2 wget gnupg ca-certificates apt-transport-https \
      software-properties-common \
      && bash ffmpeg-build.sh \
      && apt-get remove -y automake asciidoc libtool \
      && apt-get autoremove -y \
      && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

# RUN echo '@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing' | \
#           tee -a /etc/apk/repositories \
#     && apk add aria2 ncftp python3 curl-dev libmcrypt-dev \
#             cadaver openssh-client rabbitmq-server@testing erlang ffmpeg
    # && apk add --update libmcrypt-dev glib-dev openssl-dev curl-dev \
    #         gobject-introspection-dev libxml2-utils aria2 ncftp python3 \
    #&& apk add --virtual .build alpine-sdk libtool yasm automake asciidoc nasm \
    #&& bash ffmpeg-build.sh \
    #&& apk del .build \
    #&& rm -rf /tmp/* /var/tmp/

# RUN wget -O - "https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc" | apt-key add - \
#     && echo "deb http://dl.bintray.com/rabbitmq-erlang/debian stretch erlang-21.x" >/etc/apt/sources.list.d/bintray.erlang.list \
#     && apt update -y && apt install -y erlang-base \
#       erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
#       erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
#       erlang-runtime-tools erlang-snmp erlang-ssl \
#       erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl \
#     && wget -O -  https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.deb.sh | bash \
#     && apt update -y && apt install -y rabbitmq-server \
#     && apt-get autoremove -y \
#     && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

# wget https://packages.erlang-solutions.com/erlang-solutions_1.0_all.deb \
#     && dpkg -i erlang-solutions_1.0_all.deb \
#     && rm erlang-solutions_1.0_all.deb \
#     && wget -O - "https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc" | apt-key add - \
#     && add-apt-repository 'deb https://dl.bintray.com/rabbitmq/debian bionic erlang' \
#     && apt update \
#     && apt install -y erlang-nox

RUN apt update && apt install -y --no-install-recommends aria2 ncftp python3 python3-pip libffms2-dev \
      && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/
#    cadaver openssh-client \

ADD docker/otrtool-build.sh docker/keyframe-list-build.sh keyframe-list/keyframe-list.c ./
#ADD https://api.github.com/repos/otrtool/otrtool/git/refs/heads/master /dev/null
#RUN apk add --virtual .build autoconf automake libtool ffmpeg-dev \
RUN apt update && apt install -y build-essential automake libtool memcached \
    && bash otrtool-build.sh \
    && bash keyframe-list-build.sh \
    && apt-get autoremove -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#    && apk del .build

ADD docker/crontab /etc/cron.d/sync-keys-cron

ADD requirements.txt run.sh ./
RUN python3 -m pip install --upgrade pip setuptools wheel pillow && python3 -m pip install --upgrade -r requirements.txt

WORKDIR "$wwwdir"
ADD docker/uwsgi_params docker/uwsgi.ini "$wwwdir/"
# RUN chown www-data:www-data -R "$wwwdir" && \
#     mkdir -p /usr/lib/rabbitmq/ && chown -R rabbitmq /usr/lib/rabbitmq/
ADD ./ "$REPO_DIR"
WORKDIR "$REPO_DIR"

EXPOSE 80
#CMD ["bash", "/root/run.sh"]
CMD ["uwsgi", "$wwwdir/uwsgi.ini"]
