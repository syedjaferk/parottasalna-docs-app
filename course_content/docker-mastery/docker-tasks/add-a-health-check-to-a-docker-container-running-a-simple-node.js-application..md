# Add a health check to a Docker container running a simple Node.js application.

### Question

Add a health check to a Docker container running a simple Node.js application. The health check should verify that the application is running and accessible.

Sample Healthcheck API in node.js,

`app.js`

```javascript
// app.js
const express = require('express');
const app = express();
 
// A simple route to return the status of the application
app.get('/health', (req, res) => {
    res.status(200).send('OK');
});
 
// Example main route
app.get('/', (req, res) => {
    res.send('Hello, Docker!');
});
 
// Start the server on port 3000
const port = 3000;
app.listen(port, () => {
    console.log(`App is running on http://localhost:${port}`);
});
```

### Solution

#### Step 1: Create a Dockerfile

Create a Dockefile to containerize the node app. It also should include a health check command. [https://docs.docker.com/reference/dockerfile/#healthcheck](https://docs.docker.com/reference/dockerfile/#healthcheck)

```docker
# Use an official Node.js runtime as a parent image. 
# We are using slim version, so that i can install curl.
FROM node:14-slim

# Install curl
RUN apt-get update && apt-get install -y curl

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY package*.json ./
COPY app.js ./

# Install any needed packages
RUN npm install

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the application
CMD [ "node", "app.js" ]

# Add a HEALTHCHECK instruction
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:3000/health || exit 1

```

* `HEALTHCHECK`: The health check is added at the end of the Dockerfile. It checks the `/health` endpoint of your application every 30 seconds.
* `--interval=30s`: Check the health every 30 seconds.
* `--timeout=5s`: If the health check takes longer than 5 seconds, it’s considered a failure.
* `--start-period=5s`: Wait 5 seconds before starting the first health check.
* `--retries=3`: If the health check fails 3 consecutive times, the container is considered unhealthy.

#### Step 2: Build and Run the Docker Image

First, build the Docker image,

```bash
docker build -t node-app .
```


![](/_assets/image-38.png)


Then, run the container,

```bash
docker run -d --name my-node-app -p 3000:3000 node-app
```

#### Step 3: Verify the Health Check

To check the status of the container’s health, run

```bash
docker ps
```

In the output, you should see a `STATUS` column that will change from `starting` to `healthy` once the health check passes.


![](/_assets/image-39.png)
