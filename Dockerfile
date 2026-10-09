FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Static files are baked into the image; the key is only needed to import settings.
RUN SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput \
    && useradd --system --uid 1000 --create-home portal \
    && mkdir -p /app/docs_build /app/course_content \
    && chown -R portal:portal /app/docs_build \
    && chmod +x deploy/docker/entrypoint.sh

USER portal
EXPOSE 8000

ENTRYPOINT ["deploy/docker/entrypoint.sh"]
# 3 processes × 4 threads: a slow request (blog render, sitemap) no longer blocks a whole worker.
CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "4", "--worker-class", "gthread", "--access-logfile", "-"]
