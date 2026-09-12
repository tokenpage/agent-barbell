# Stage 1: build
FROM node:25.9.0 AS build

WORKDIR /app
COPY makefile .
COPY package.json .
COPY package-lock.json .
RUN make install

COPY . .
RUN make build

# Stage 2: Serve with nginx
FROM ghcr.io/kibalabs/app-serve:latest
COPY --from=build /app/dist /usr/share/nginx/html
