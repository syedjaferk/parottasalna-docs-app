# Running ‘Hello, World!’ with BusyBox: A Docker Adventure


<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/n2nD-vCasL8" title="YouTube video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>


Once upon a time in the city of Athipati, there was a young coder named Arivanandham. Arivanandham had recently heard whispers of a magical tool called Docker, which promised to simplify the process of running applications. Eager to learn more, **Arivanandham** decided to embark on a quest—a quest to run the famous “Hello, World!” using the mysterious BusyBox Docker image.

Today, we’re going to take our first step by creating and running a container. And what better way to start than with a tiny yet powerful image called BusyBox? Let’s dive in and explore how to run our first container using BusyBox.

### **Step 1: Discovering BusyBox on Docker Hub**

Our journey begins at the Docker Hub, the vast library of images ready to be transformed into containers. Let’s search for “BusyBox” on Docker Hub.

Upon searching, you’ll find the official BusyBox repository at the top. BusyBox is renowned for its compact size—about 1 megabyte—which makes it an excellent choice for quick downloads and speedy container spins.


![](/_assets/image-5.png)


### **Step 2: Exploring BusyBox Tags**

Before we proceed, let’s check out the **Tags** tab on the BusyBox page. Tags represent different versions of the image. We’re going to pick **tag 1.36** for our container. This specific tag will be our guide in this Docker adventure.


![](/_assets/image-6.png)


### **Step 3: Setting Up Your Docker Environment**

To start, we need to open a terminal. If you’re on Docker for Mac, Docker for Windows, or Linux, you can simply open your default terminal. If you’re using Docker Toolbox, open the Docker Quickstart Terminal.

### **Step 4: Checking Local Images**

When you instruct Docker to create a container, it first checks your local system to see if the image is already available. Let’s verify what images we currently have:

```bash
docker images
```

If this is your first time, you’ll see that there are no images available yet. But don’t worry; we’re about to change that.


![](/_assets/image-7.png)


### **Step 5: Running Your First Container**

Now, let’s run our first container! We’ll use the `docker run` command, specifying the BusyBox image and tag 1.36. We’ll also tell Docker to execute a simple command: `echo "Hello, World!"`.

```bash
docker run busybox:1.36 echo "Hello, World!"
```


![](/_assets/image-8.png)


Here’s what happens next:

* Docker checks for the BusyBox 1.36 image locally.
* If it’s not found, Docker will download the image from the remote repository.
* Once the image is downloaded, Docker creates and runs the container.

And just like that, you should see the terminal output:

> Hello, World!

Congratulations! You’ve just run your first Docker container.

### **Step 6: Verifying the Image Download**

Let’s run the `docker images` command again:

```bash
docker images
```

You’ll now see the BusyBox 1.36 image listed. The image has a unique ID, confirming that it’s stored locally on your system.


![](/_assets/image-9.png)


### **Step 7: Running the Container Again**

Now that we have the BusyBox image locally, let’s run the same container again

```bash
docker run busybox:1.36 echo "Hello, World!"
```

This time, notice how quickly the command executes. Docker uses the local image, skipping the download step, and instantly spins up the container.


![](/_assets/image-10.png)


### **Step 8: Exploring the Container’s File System**

Let’s try something new. We’ll list all the contents in the root directory of the BusyBox container

```bash
docker run busybox:1.36 ls /
```

You’ll see Docker output the list of all directories and files at the root level of the container.

### **Step 9: Running a Container in Interactive Mode**

To dive deeper, we can run the container in an interactive mode, which allows us to interact with the container as if it were a tiny, isolated Linux system. We’ll use the `-i` (interactive) and `-t` (pseudo-TTY) flags.

```bash
docker run -it busybox:1.36
```

Now you’re inside the container! Try running commands like `ls` to see the contents. You can even create a new file

```bash
touch a.txt
ls
```

You’ll see `a.txt` listed in the output. To exit the container, simply type `exit`.

### **Step 10: Understanding Container Lifecycle**

It’s important to note that once you exit a container, it shuts down. If you run the container again using the same command, Docker spins up a brand-new instance. The file you created earlier (`a.txt`) won’t be there because each container instance is ephemeral, meaning it doesn’t retain data from previous runs unless you explicitly save it.

And there you have it! You’ve successfully created, explored, and understood your first Docker container using the BusyBox image. This is just the beginning of what you can achieve with Docker. As you continue your journey, you’ll discover how containers can simplify development, testing, and deployment, all while keeping your environment clean and isolated.
