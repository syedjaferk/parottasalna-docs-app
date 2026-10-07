# Pull the nginx image from Docker Hub and run it as a container. Map port 80 of the container to port

### Question

Pull the `nginx` image from Docker Hub and run it as a container. Map port 80 of the container to port 8080 of your host.

### Solution

```sh
docker run -p 8080:80 nginx
```
