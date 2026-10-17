# Docker Mastery

Understand containers through stories and hands-on labs: Docker architecture, images and containers, Dockerfiles, port mapping, volumes and practical tasks.

## How each session works

1. **The big idea**: the topic in plain words, with an everyday example.
2. **A picture**: a diagram of the idea.
3. **Real commands**: every command was run on Docker 28 and the output you see is what it printed.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then open the solution.
6. **Practice**: a quiz for the session.

:::{tip}
You need Docker installed and running (`docker version` should show a client **and** a server). Work in a
scratch folder, and clean up with `docker rm -f NAME` when an exercise is done.
:::

```{raw} html
:file: diagrams/course-flow.html
```

```{toctree}
:maxdepth: 1
:caption: Sessions

sessions/01-why-containers
sessions/02-docker-architecture
sessions/03-images-and-containers
sessions/04-running-containers
sessions/05-background-logs-inspect
sessions/06-port-mapping
sessions/07-dockerfile
sessions/08-volumes
```

```{toctree}
:maxdepth: 2
:caption: Original stories (reference)

Virtual Machine and The Grand House <introduction>
The Tale of Magic Kitchen : A Docker Architecture <the-tale-of-magic-kitchen-a-docker-architecture>
Virtual Machine vs Containers <virtual-machine-vs-containers>
The Digital Tea Kadai – Client Server Architecture & Docker <the-digital-tea-kadai-client-server-architecture-and-docker>
The Bakery, Recepies, Dough & Cookies – Registry, Repository, Images, Containers <the-bakery-recepies-dough-and-cookies-registry-repository-images-containers>
Running ‘Hello, World!’ with BusyBox: A Docker Adventure <running-hello-world-with-busybox-a-docker-adventure>
Diving Deeper into Docker with Detached Mode, Naming, and Inspections <diving-deeper-into-docker-with-detached-mode-naming-and-inspections>
Tomcat: Exploring Docker Port Mapping and Logs <tomcat-exploring-docker-port-mapping-and-logs>
The Building Blocks – Detailed Structure of a Dockerfile <the-building-blocks-detailed-structure-of-a-dockerfile>
Docker Volumes Explained: A Quick Guide <docker-volumes-explained-a-quick-guide>
```

```{toctree}
:maxdepth: 2
:caption: Docker Tasks

Pull the nginx image from Docker Hub and run it as a container. Map port 80 of the container to port <docker-tasks/pull-the-nginx-image-from-docker-hub-and-run-it-as-a-container.-map-port-80-of-the-container-to-port>
Create a Dockerfile for a simple Node.js application that serves “Hello World” on port 3000. <docker-tasks/create-a-dockerfile-for-a-simple-node.js-application-that-serves-hello-world-on-port-3000.>
Run a container from the ubuntu image and start an interactive shell session inside it. <docker-tasks/run-a-container-from-the-ubuntu-image-and-start-an-interactive-shell-session-inside-it.>
Create a Dockerfile for a Go application that uses multi-stage builds to reduce the final image size <docker-tasks/create-a-dockerfile-for-a-go-application-that-uses-multi-stage-builds-to-reduce-the-final-image-size>
Create a Docker volume and use it to persist data for a MySQL container. <docker-tasks/create-a-docker-volume-and-use-it-to-persist-data-for-a-mysql-container.>
Add a health check to a Docker container running a simple Node.js application. <docker-tasks/add-a-health-check-to-a-docker-container-running-a-simple-node.js-application.>
```

```{toctree}
:maxdepth: 2
:caption: Docker Live

Docker Live | Meet & Greet <https://www.youtube.com/live/lOvMWN64CkM?si=XpYJelt8-nLsNJy0>
Docker Live | Need of Docker <https://www.youtube.com/live/owfv4r32i_g?si=Y2xVfC-NfnBBt2iJ>
Docker Live | Bonding of Image & Container, Client Server Architecture <https://www.youtube.com/live/8EgJcMgr7ig?si=BRf0jHIfuQX-SvdZ>
Docker Live | Docker Logs, Remove, Port Mapping <https://www.youtube.com/live/dQpj4M4unbo?si=M0gG7C_1_a5s_Bci>
Docker Live | Dockerize a Flask Application <https://www.youtube.com/live/LFunyCQz5C0?si=OaJY_JHaOpkcTGPB>
```
