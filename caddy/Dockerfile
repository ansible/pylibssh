FROM alpine:3.7
MAINTAINER Paul Kehrer

# Increment this to blow away the docker cache
ENV CACHE_BUSTER 2

RUN apk add --no-cache tar curl libcap

RUN curl -sSL \
      --header "Accept: application/tar+gzip, application/x-gzip, application/octet-stream" \
      "https://caddyserver.com/download/linux/amd64?plugins=http.prometheus" \
    | tar --no-same-owner -C /usr/bin/ -xz caddy
RUN chmod 0755 /usr/bin/caddy
RUN setcap cap_net_bind_service=+eip /usr/bin/caddy
RUN /usr/bin/caddy -version
RUN mkdir /.caddy
RUN chown nobody:nobody /.caddy

EXPOSE 80 443 2015

ADD Caddyfile /etc/Caddyfile

USER nobody

ENTRYPOINT ["/usr/bin/caddy"]
CMD ["--conf", "/etc/Caddyfile", "--log", "stdout"]
