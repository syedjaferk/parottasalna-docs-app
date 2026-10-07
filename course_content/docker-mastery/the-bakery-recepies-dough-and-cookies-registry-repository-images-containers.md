# The Bakery, Recepies, Dough & Cookies – Registry, Repository, Images, Containers

In the bustling town of Tambaram, there was a famous factory known for its delicious cookies. This factory had a unique and modern way of making and distributing its cookies, using a system inspired by Docker’s architecture.



### **The Recipe Registry**

At the heart of the cookie-making process was the **Recipe Registry**, a giant digital library that stored all the cookie recipes. This registry was like a magical cookbook, holding secrets to every type of cookie imaginable: chocolate chip, oatmeal raisin, and even double fudge delight.

* **Purpose**: The Recipe Registry ensured that everyone had access to the latest and greatest recipes. Bakers from all around the world could upload new recipes or download existing ones to make their own cookies.


![](/_assets/image-28.png)


### **The Cookie Repository**

Each type of cookie had its own **Cookie Repository** within the Recipe Registry. These repositories were specialized sections where all the different variations of a particular cookie recipe were stored.

* **Example**: The chocolate chip cookie repository contained recipes for classic, vegan, gluten-free, and extra gooey versions. Each version was labeled with a tag, like `classic`, `vegan`, or `gooey`.


![](/_assets/image-29.png)


### **The Image: A Perfect Cookie Dough**

In the factory, the term “Image” referred to the perfect **cookie dough** that was ready to be baked into cookies. Each image was a complete package containing the recipe, ingredients, and instructions needed to make the cookies.

* **Characteristics**: Just like a Docker image, the cookie dough was consistent and repeatable. No matter how many times you used the recipe, you always got the same delicious dough, ready to be baked.


![](/_assets/image-30.png)


### **The Container: Freshly Baked Cookies**

Once the cookie dough was prepared, it was placed into a **Container**, representing a batch of freshly baked cookies. Each container was like a magical oven that turned the dough into cookies.

* **Isolation**: Each container baked cookies independently, ensuring that the flavor and quality were perfect every time. Bakers could create multiple containers from the same dough image, producing countless batches of cookies.


![](/_assets/image-31.png)


### **The Cookie Delivery System**

With the help of the Recipe Registry, Cookie Repository, Images, and Containers, the factory had an efficient **Cookie Delivery System**. This system allowed the factory to distribute its cookies all over Tambaram and beyond.

* **Scalability**: If a bakery needed more cookies, they simply created more containers using the same dough image, ensuring everyone had enough cookies to enjoy.

Let’s try directly in to the concepts,

### Registry

* **Definition**: A Docker Registry is a storage and content delivery system that holds Docker images.
* **Purpose**: It is used to manage where Docker images are stored and distributed from.
* **Examples**: Docker Hub (the default public registry), Amazon ECR, Google Container Registry, and Azure Container Registry.
* **Functionality**: Registries can be public or private. They store Docker images and provide an interface to push (upload) or pull (download) these images to and from repositories.


![](/_assets/image-32.png)


Docker Hub is the default public registry used by Docker. Here are examples of Docker Hub registry links:

* **Official Image**: `docker pull nginx`
* Link:[https://hub.docker.com/\_/nginx](https://hub.docker.com/_/nginx)

**Community Image**: `docker pull username/repository:tag`

* Link:[https://hub.docker.com/r/username/repository](https://hub.docker.com/r/username/repository) (replace `username/repository` with the actual user and repository name)

### Repository

* **Definition**: A Docker Repository is a collection of related Docker images, usually providing different versions of the same application or service.
* **Purpose**: Repositories organize and manage multiple images of an application or service.
* **Structure**: A repository may contain multiple tagged versions of an image. For example, `myapp:latest` and `myapp:v1.0` might be two tags in the same repository.
* **Functionality**: Users can push images to a repository and pull images from a repository. Tags are used to differentiate between different versions of an image.

**Official Repositories**

* **Nginx**:
  * Command: `docker pull nginx:latest`
  * Repository Link:[https://hub.docker.com/\_/nginx](https://hub.docker.com/_/nginx)
* **Ubuntu**:
  * Command: `docker pull ubuntu:latest`
  * Repository Link:[https://hub.docker.com/\_/ubuntu](https://hub.docker.com/_/ubuntu)

**Community Repositories**

* **Node.js (Official Node.js Images)**:
  * Command: `docker pull node:latest`
  * Repository Link:[https://hub.docker.com/\_/node](https://hub.docker.com/_/node)
* **Jenkins (Community Image)**:
  * Command: `docker pull jenkins/jenkins:lts`
  * Repository Link:[https://hub.docker.com/r/jenkins/jenkins](https://hub.docker.com/r/jenkins/jenkins)

**User-Specific Repositories**

* **Example User Repository**:
  * Command: `docker pull username/repository:tag`
  * Repository Link:[https://hub.docker.com/r/username/repository](https://hub.docker.com/r/username/repository) (replace `username/repository` with the actual user and repository name)


![](/_assets/image-33.png)


### Images

* **Definition**: A Docker Image is a lightweight, standalone, executable package that includes everything needed to run a piece of software: code, runtime, libraries, environment variables, and configuration files.
* **Purpose**: Images are used to create containers. They provide a portable and consistent runtime environment.
* **Immutability**: Images are immutable; once created, they do not change. If updates are needed, a new image version is created.
* **Layers**: Images are built up from a series of layers, where each layer represents an instruction in the image’s Dockerfile.

For example, Dockerfile will comprises of the layers of instructions. [https://hub.docker.com/layers/library/postgres/12.20-bullseye/images/sha256-2092f4af9ad9fff76e8d0b7c04d8c62b561e44c21a850d4a028124426046f6fa?context=explore](https://hub.docker.com/layers/library/postgres/12.20-bullseye/images/sha256-2092f4af9ad9fff76e8d0b7c04d8c62b561e44c21a850d4a028124426046f6fa?context=explore)

Sample dockerfile for postgres, [https://github.com/docker-library/postgres/blob/805329e7a64fad212a5d4b07abd11238a9beab75/17/bookworm/Dockerfile](https://github.com/docker-library/postgres/blob/805329e7a64fad212a5d4b07abd11238a9beab75/17/bookworm/Dockerfile)


![](/_assets/image-34.png)


#### Containers

* **Definition**: A Docker Container is a runnable instance of a Docker image. It is a lightweight, standalone, and executable package of software that includes everything needed to run it.
* **Purpose**: Containers provide a consistent environment for applications, allowing them to run reliably regardless of where they are deployed.
* **Isolation**: Containers are isolated from each other and the host system, but they can communicate with each other through well-defined channels.
* **Lifecycle**: Containers can be created, started, stopped, moved, or deleted using Docker commands.


![](/_assets/image-35.png)


### Relationship Between Concepts

* **Registry and Repository**: A Docker registry can host multiple repositories. Each repository can contain multiple images with different tags.
* **Repository and Images**: A repository serves as a namespace for images. For example, `myrepo/myapp` can contain different image tags like `v1.0`, `v2.0`, etc.
* **Images and Containers**: Containers are running instances of images. You can run multiple containers from the same image.
