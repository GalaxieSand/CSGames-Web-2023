FROM ubuntu:18.04
RUN apt-get update && apt-get install -y nginx python3 python3-pip gettext-base

RUN mkdir /idserver

WORKDIR /idserver
ADD requirements.txt /idserver/requirements.txt
RUN pip3 install -r requirements.txt

ADD . /idserver
RUN cp IdServer /etc/nginx/sites-available/IdServer
RUN ln -s /etc/nginx/sites-available/IdServer /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

ENV PYTHONPATH /idserver/pylib

RUN chmod a+x start.sh
CMD ["./start.sh"]
