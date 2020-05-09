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


RUN apt update && apt install -y --no-install-recommends aria2 ncftp python3 python3-pip libffms2-dev \
      && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/

ADD docker/otrtool-build.sh docker/keyframe-list-build.sh keyframe-list/keyframe-list.c ./
RUN apt update && apt install -y build-essential automake libtool uwsgi uwsgi-plugin-python3 \
    && bash otrtool-build.sh \
    && bash keyframe-list-build.sh \
    && apt-get autoremove -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD docker/crontab /etc/cron.d/sync-keys-cron

ADD docker/uwsgi_params docker/uwsgi.ini docker/requirements "$wwwdir/"

WORKDIR "$REPO_DIR"
RUN python3 -m pip install --upgrade pip setuptools wheel pillow virtualenv && \
    virtualenv env && . ./env/bin/activate && \
    python3 -m pip install --upgrade -r "$wwwdir/requirements.txt"

ADD ./ "$REPO_DIR"

RUN chown www-data:www-data -R "$wwwdir"

EXPOSE 80
CMD ["uwsgi", "$wwwdir/uwsgi.ini"]
