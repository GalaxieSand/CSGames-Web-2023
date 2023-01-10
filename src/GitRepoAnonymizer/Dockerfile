FROM ubuntu:18.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y git

RUN mkdir work_dir

ADD requirements.txt /gitminer/requirements.txt
WORKDIR /gitminer
RUN pip3 install -r requirements.txt

ADD . /gitminer

RUN cp git-filter-branch.tpl /usr/lib/git-core/git-filter-branch.tpl
ENV FILTER_BRANCH_PATH /usr/lib/git-core/git-filter-branch
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8
RUN chmod a+w /usr/lib/git-core/git-filter-branch

ENV PYTHONPATH /gitminer/pylib
CMD ["python3", "GitRepoAnonymizer.py"]
