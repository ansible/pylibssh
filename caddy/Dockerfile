FROM alpine:3.5
MAINTAINER Paul Kehrer

ARG plugins=prometheus

RUN apk add --no-cache tar curl

RUN curl -sSL \
      --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" \
      "https://caddyserver.com/download/build?os=linux&arch=amd64&features=${plugins}" \
    | tar --no-same-owner -C /usr/bin/ -xz caddy
RUN chmod 0755 /usr/bin/caddy
RUN /usr/bin/caddy -version

EXPOSE 80 443 2015

ADD Caddyfile /etc/Caddyfile

ENTRYPOINT ["/usr/bin/caddy"]
CMD ["--conf", "/etc/Caddyfile", "--log", "stdout"]
