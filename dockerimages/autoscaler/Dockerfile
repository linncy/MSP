FROM python:3.5-alpine
ADD . /code
WORKDIR /code
RUN apk update supervisor
RUN apk add supervisor
RUN mkdir -p /var/log/supervisor
ADD supervisord.conf /etc/supervisord.conf
RUN pip3 install -r requirements.txt
EXPOSE 5900 5900
CMD ["/usr/bin/supervisord"]
