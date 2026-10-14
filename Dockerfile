FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY setup.py README.md ./
COPY src ./src
RUN pip install --no-cache-dir --no-deps .

FROM base AS test
COPY requirements-dev.txt .coveragerc pytest.ini ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests ./tests
RUN python -m compileall -q src/myapp
CMD ["sh", "-c", "mkdir -p reports && python -m pytest --junitxml=reports/junit.xml --cov --cov-report=term-missing --cov-report=xml:reports/coverage.xml && python -m build --no-isolation"]

FROM base AS runtime
LABEL org.opencontainers.image.source="https://github.com/vanviet2k6-creator/my-python-app"
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=12 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=2)" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "myapp.web:create_app()"]
