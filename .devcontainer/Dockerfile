FROM python:3.12-alpine3.19
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

#Install all dependencies.
RUN apk add --no-cache postgresql-libs postgresql-client gettext zlib libjpeg libwebp libxml2-dev libxslt-dev openldap git yarn

#Print all logs without buffering it.
ENV PYTHONUNBUFFERED 1

#This port will be used by gunicorn.
EXPOSE 8000

#This port will be used by vue
EXPOSE 8080

ENV UV_COMPILE_BYTECODE=1

ENV UV_LINK_MODE=copy

RUN \
    if [ `apk --print-arch` = "armv7" ]; then \
    printf "[global]\nextra-index-url=https://www.piwheels.org/simple\n" > /etc/pip.conf ; \
    fi
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev zlib-dev jpeg-dev libwebp-dev openssl-dev libffi-dev cargo openldap-dev python3-dev && \
    echo -n "INPUT ( libldap.so )" > /usr/lib/libldap_r.so

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --dev && \
    apk --purge del .build-deps