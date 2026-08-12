FROM gcr.io/oss-fuzz-base/base-builder-python

RUN pip3 install atheris

COPY . $SRC/actions_ex
COPY build.sh $SRC/

ENV PYTHONPATH=$SRC/actions_ex

WORKDIR $SRC/actions_ex
