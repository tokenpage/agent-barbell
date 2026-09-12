FROM python:3.14.4-slim

RUN apt-get update && apt-get install --yes --no-install-recommends make git

WORKDIR /app
COPY makefile .

COPY pyproject.toml .
RUN make install

COPY . .

EXPOSE 5100
CMD ["make", "start-prod"]
