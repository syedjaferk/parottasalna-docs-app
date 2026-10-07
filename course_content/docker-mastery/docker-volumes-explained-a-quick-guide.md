# Docker Volumes Explained: A Quick Guide


<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/39kh59XF-1I" title="YouTube video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>


Docker containers are temporary by design, but often we need to keep data safe and available between container runs.&#x20;

This is where **Docker volumes** come in. Volumes allow you to persist and share data across containers. In this guide, we’ll explore,

* Types of Docker volumes: **Named Volumes** and **Bind Mounts**
* How to create and use them

### **Types of Docker Volumes**

There are two main types of Docker volumes,

#### 1. Named Volumes (Un Binded Volume)

Docker manages these volumes and stores them in its own storage area, making them ideal for persisting data across containers.

#### Creating a Named Volumes&#x20;

```bash
docker volume create my_named_volume
```

#### Using a Named Volume in a Container

```bash
docker run -v my_named_volume:/app/data busybox:1.36
```

#### 2. Bind Mounts (Folder Based)

Bind mounts link a specific directory on the host to a container. This gives you control over exactly which files are shared, but it’s less portable.

**Using a Bind Mount:**

```bash
docker run -v /path/to/folder/on/host:/app/data busybox:1.36
```

### **Key Differences Between Named Volumes and Bind Mounts**

| Feature         | Named Volumes                               | Bind Mounts                                      |
| --------------- | ------------------------------------------- | ------------------------------------------------ |
| **Managed By**  | Docker                                      | Host System                                      |
| **Location**    | Docker’s storage directory                  | Specific path on the host machine                |
| **Portability** | Highly portable                             | Tied to the host environment                     |
| **Use Case**    | Persistent data across container lifecycles | Development or when direct host access is needed |

**Filtering Containers by Volume**

Sometimes you want to find containers using a specific volume.

```bash
docker ps -a --filter volume=my_named_volume
```
