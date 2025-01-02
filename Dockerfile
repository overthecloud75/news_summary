FROM python:3.12.6-alpine3.20
ARG REGISTRY

RUN apk update
RUN apk add --no-cache tzdata
RUN apk add chromium chromium-chromedriver

RUN ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

RUN mkdir /webApp
WORKDIR /webApp

COPY ./ ./

RUN adduser -D ti   
RUN chown -R ti:ti .
RUN chmod -R 744 .

USER ti

RUN pip3 install --extra-index-url ${REGISTRY} -r requirements.txt

CMD ["python3", "main.py"]