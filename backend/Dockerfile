# ---- build stage: install dependencies into a virtualenv ----
FROM python:3.14-slim AS build
ENV PIP_NO_CACHE_DIR=1
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- runtime stage: small image, no build tools ----
FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/venv/bin:$PATH"
RUN useradd --create-home app
COPY --from=build /venv /venv
WORKDIR /app
COPY --chown=app:app . .
RUN mkdir -p /app/staticfiles && chown app:app /app/staticfiles
USER app
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "3", "--timeout", "30", "--access-logfile", "-"]