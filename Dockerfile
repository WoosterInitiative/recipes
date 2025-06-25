FROM python:3.12-alpine3.19
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

#Install all dependencies.
RUN apk add --no-cache postgresql-libs postgresql-client gettext zlib libjpeg libwebp libxml2-dev libxslt-dev openldap git

#Print all logs without buffering it.
ENV PYTHONUNBUFFERED 1

ENV DOCKER true

#This port will be used by gunicorn.
EXPOSE 8080

#Create app dir and install requirements.
RUN mkdir /opt/recipes
WORKDIR /opt/recipes

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev zlib-dev jpeg-dev libwebp-dev openssl-dev libffi-dev cargo openldap-dev python3-dev xmlsec-dev xmlsec build-base  && \
    echo -n "INPUT ( libldap.so )" > /usr/lib/libldap_r.so

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

RUN apk --purge del .build-deps

#Copy project and execute it.
COPY . ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# commented for now https://github.com/TandoorRecipes/recipes/issues/3478
#HEALTHCHECK --interval=30s \
#            --timeout=5s \
#            --start-period=10s \
#            --retries=3 \
#            CMD [ "/usr/bin/wget", "--no-verbose", "--tries=1", "--spider", "http://127.0.0.1:8080/openapi" ]

# collect information from git repositories
RUN uv run version.py
# delete git repositories to reduce image size
RUN find . -type d -name ".git" | xargs rm -rf

RUN chmod +x boot.sh
ENTRYPOINT ["/opt/recipes/boot.sh"]
