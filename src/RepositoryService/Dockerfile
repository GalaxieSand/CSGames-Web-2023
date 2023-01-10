FROM ubuntu:18.04
RUN apt-get update && apt-get install -y git nginx python3 python3-pip

RUN mkdir /repositoryservice
WORKDIR /repositoryservice
ADD requirements.txt /repositoryservice/requirements.txt
RUN pip3 install -r requirements.txt

ADD . /repositoryservice

WORKDIR /repositoryservice

RUN cp RepositoryService /etc/nginx/sites-available/RepositoryService
RUN ln -s /etc/nginx/sites-available/RepositoryService /etc/nginx/sites-enabled
RUN rm /etc/nginx/sites-enabled/default

ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /repositoryservice/pylib

RUN chmod a+x start.sh

CMD ["./start.sh"]
