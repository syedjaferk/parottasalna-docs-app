# Create a Dockerfile for a Go application that uses multi-stage builds to reduce the final image size

### Question

Create a Dockerfile for a Go application that uses multi-stage builds to reduce the final image size. The application should print “Hello Docker”. Sample Go code.

`app.go`

```go
package main
 
import "fmt"
 
func main() {
    fmt.Println("Hello Docker")
}
```

### Solution

`Dockerfile`

```docker
FROM golang:1.21.0-alpine

WORKDIR /app

COPY app.go /app
CMD ["go", "run", "app.go"]


```

Build the image,&#x20;

```bash
docker build -f Dockerfile -t go_image:v1.1.0 .
```


![](/_assets/image-4.png)


```bash
docker run go_image:v1.1.0
```


![](/_assets/image-37.png)


This is a normal image, When we dive into it we can see its 221MB


![](/_assets/image.png)


#### Let's try using the multistage build,&#x20;

```docker
FROM golang:1.21.0-alpine AS build
WORKDIR /app
COPY app.go .
RUN go build -o myapp app.go

FROM alpine:3.18
WORKDIR /app
COPY --from=build /app/myapp .
CMD ["./myapp"]

```

Build the image,&#x20;

```
docker build -f Dockerfile -t go_image_multi_stage_build:v1.1.0 .
```


![](/_assets/image-1.png)


Let's dive into the image,&#x20;


![](/_assets/image-2.png)


Now we can see its been reduced from 221MB to 9.2MB.&#x20;
