FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY apps /app/apps
COPY config /app/config
COPY templates /app/templates
COPY static /app/static
COPY manage.py /app/manage.py

RUN pip install --upgrade pip && pip install .

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
