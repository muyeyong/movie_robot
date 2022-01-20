FROM python:3.8.12-slim
LABEL title="影视剧机器人"
LABEL description="可以自动从豆瓣用户的想看、在看、看过列表中自动获取电影，并通过Radarr、Sonarr管理数据"
LABEL authors="Yong"
# 设置任务轮询执行时间
ENV DOWNLOAD_CRON='0 2,10,12,14,16,19,21 * * *'  
COPY src /app/src
COPY douban_movie_download.py /app
COPY requirements.txt /app
COPY user_config.yml /app
WORKDIR /app
VOLUME /data
ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y tzdata \
    && apt-get install -y cron \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip \
    && pip install -r requirements.txt
RUN echo "$DOWNLOAD_CRON /usr/local/bin/python /app/douban_movie_download.py -w /data >> /var/log/cron.log 2>&1" > /etc/cron.d/download-cron
RUN chmod +x /etc/cron.d/download-cron
RUN crontab /etc/cron.d/download-cron
RUN touch /var/log/cron.log
CMD python /app/douban_movie_download.py -w /data && cron && tail -f /var/log/cron.log