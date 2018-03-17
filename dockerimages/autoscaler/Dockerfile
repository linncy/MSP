FROM python:3.5-alpine
ADD . /code
WORKDIR /code
RUN apk update supervisor
RUN apk add supervisor
RUN echo "@community http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk add --update --no-cache ca-certificates gcc g++ curl openblas-dev@community
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN mkdir -p /var/log/supervisor
ADD supervisord.conf /etc/supervisord.conf
RUN pip3 install --no-cache-dir --disable-pip-version-check -r requirements.txt
EXPOSE 5900 5900
CMD ["/usr/bin/supervisord"]
