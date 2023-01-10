FROM ubuntu:18.04
RUN apt-get update && apt-get install -y git nginx python3 python3-pip

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN mkdir /snippetsservice
WORKDIR /snippetsservice
ADD . /snippetsservice
WORKDIR /snippetsservice

RUN cp SnippetsService /etc/nginx/sites-available/SnippetsService
RUN ln -s /etc/nginx/sites-available/SnippetsService /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /snippetsservice/pylib

RUN chmod a+x start.sh

CMD ["./start.sh"]
