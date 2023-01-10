FROM ubuntu:18.04
RUN apt-get update && apt-get install -y nginx python3 python3-pip gettext-base

ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN rm /requirements.txt

RUN mkdir /webdocs
WORKDIR /webdocs

ADD . /webdocs
RUN cp webdocs /etc/nginx/sites-available/webdocs
RUN ln -s /etc/nginx/sites-available/webdocs /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

RUN chmod a+x start.sh
CMD ["./start.sh"]
