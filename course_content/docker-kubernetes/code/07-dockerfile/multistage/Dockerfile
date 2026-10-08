# Stage 1: build
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY main.go .
RUN go mod init hello && CGO_ENABLED=0 go build -o /hello .

# Stage 2: run
FROM scratch
COPY --from=build /hello /hello
ENTRYPOINT ["/hello"]
