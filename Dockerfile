FROM python:3.10.12-slim-bullseye

ENV APP_CODE_DIR /code
ENV REQ_TXT requirements.txt

WORKDIR $APP_CODE_DIR

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

COPY $REQ_TXT $REQ_TXT

RUN python -m pip install -U pip pip-tools
RUN python -m pip install -r "$REQ_TXT"

COPY . $APP_CODE_DIR

EXPOSE 5808

RUN ["chmod", "+x", "tests/integration_test.sh"]
CMD ["python", "application/main.py"]
