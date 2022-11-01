FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

ENV PYTHONPATH=/app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false


COPY . /app

RUN bash -c "poetry install --no-root --only main"

CMD [ ".venv/bin/python", "main.py"]