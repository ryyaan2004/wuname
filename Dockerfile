FROM python:3.6-slim-stretch
#RUN apk add --no-cache gcc \
#                       musl-dev \
#                       python3-dev \
#                       gpgme-dev \
#                       libc-dev \
#                       linux-headers \
#                       && pip install pipenv
RUN pip install pipenv

COPY Pipfile /opt
WORKDIR /opt
RUN pipenv lock --requirements > requirements.txt && \
    pip install -r /opt/requirements.txt && \
    pip install gunicorn

ADD assets /opt/wuname/assets
ADD static /opt/wuname/static
ADD templates /opt/wuname/templates
ADD *.py /opt/wuname

WORKDIR /opt/wuname
CMD exec gunicorn -b :$PORT wuname:app
