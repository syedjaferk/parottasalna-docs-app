# Create a Dockerfile for a simple Node.js application that serves “Hello World” on port 3000.

### Question

Create a Dockerfile for a simple Node.js application that serves “Hello World” on port 3000. Build the Docker image with tag **my-node-app** and run a container. Below is the sample index.js file.

```javascript
const express = require('express');
const app = express();
 
app.get('/', (req, res) => {
    res.send('Hello World');
});
 
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
```

Tag the Docker image `my-node-app` from Task 3 with a version tag `v1.0.0`.



### Solution

`Dockerfile`

```docker
FROM node:20.13.1-alpine

WORKDIR /app

COPY index.js /app
COPY package.json /app
COPY package-lock.json /app

RUN npm i

CMD ["node", "index.js"]
```

#### Build the image

```bash
docker build -f Dockerfile -t my-node-app:v1.0.0 .
```

#### Push the image to Docker Hub

```sh
docker login
```

Then build the image with your repo name,  For eg, \`syedjaferkhub\`

```bash
docker push syedjaferkhub/my-node-app:v1.0.0
```

Eg: [https://hub.docker.com/u/syedjaferkhub](https://hub.docker.com/u/syedjaferkhub)
