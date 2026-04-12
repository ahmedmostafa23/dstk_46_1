ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION}

WORKDIR /attrition_inference

RUN echo "Hello World"

RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

ARG ENVIRONMENT1
ENV ENVIRONMENT1=${ENVIRONMENT}

COPY pyproject.toml .
COPY .python-version .
COPY uv.lock .

RUN uv sync

COPY . .

EXPOSE 8000
ENTRYPOINT ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["--log-level", "trace"]


