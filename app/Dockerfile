# syntax=docker/dockerfile:1.4

FROM --platform=$BUILDPLATFORM python:3.14.5-alpine AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /esterilizaya
COPY ./app/requirements.txt /esterilizaya
RUN apk add --no-cache --virtual \
      build-deps \ 
      cairo-dev=~1 \
      freetype-dev=~2 \
      gcc=~15 \
      g++=~15 \
      gdk-pixbuf-dev=~2 \
      harfbuzz-dev=~12 \
      jpeg-dev=~9f \
      libffi-dev=~3 \
      libxml2-dev=~2 \
      libxslt-dev=~1 \
      mariadb-dev=~11 \
      musl-dev=~1 \
      pango-dev=~1 \
      pkgconf=~2 \
      zlib-dev=~1 && \  
    pip install --no-cache-dir -r requirements.txt && \
    apk del build-deps

FROM --platform=$BUILDPLATFORM python:3.14.5-alpine AS base
WORKDIR /home/esterilizaya/code
RUN apk add --no-cache \ 
      cairo=~1 \
      curl=~8 \
      font-liberation=~2 \
      font-opensans=~0 \
      fontconfig=~2 \
      freetype=~2 \
      gdk-pixbuf=~2 \
      harfbuzz=~12 \
      jpeg=~9f \
      libffi=~3 \
      libxml2=~2 \
      libxslt=~1 \
      mariadb-connector-c-dev=~3 \
      weasyprint=~66 \
      zlib~=1

RUN adduser -S -G www-data www-data
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY ./app/ ./
# Crear los directorios iniciales
RUN mkdir -p /home/esterilizaya/media
# Cambiar los permisos de los archivos copiados
RUN chown -R www-data:www-data /home/esterilizaya/code /home/esterilizaya/media
USER www-data

FROM --platform=$BUILDPLATFORM base AS prod
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/
COPY ./config/uwsgi/uwsgi.ini /home/esterilizaya/config/uwsgi/uwsgi.ini
EXPOSE 80 443

FROM --platform=$BUILDPLATFORM base AS debug
RUN pip install --no-cache-dir django-debug-toolbar==6.*
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1
EXPOSE 8000