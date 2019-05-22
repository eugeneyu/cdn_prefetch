FROM marketplace.gcr.io/google/ubuntu1804:latest
RUN apt-get update && apt-get install -y software-properties-common ssh
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.7 python3-pip
RUN python3.7 -m pip install flask --user
RUN python3.7 -m pip install Flask-APScheduler --user
WORKDIR /root
COPY prefetch_api_aps.py ./
COPY nodes.txt ./
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["python3.7", "./prefetch_api_aps.py"]