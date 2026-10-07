# Diving Deeper into Docker with Detached Mode, Naming, and Inspections

r last adventure with Docker, we successfully ran our first container using the BusyBox image. It was a moment of triumph, seeing that “hello world” echo back at us from the depths of our new container.

Today, we delve even deeper into the Dockerverse, learning how to run containers in detached mode, name them, and inspect their inner workings.

### **The Background Wizardry: Detached Mode**

Imagine you’re a wizard, conjuring a spell to summon a creature (a.k.a. a Docker container). But what if you wanted to summon this creature to do your bidding in the background while you continued your magical studies in the foreground? This is where the art of detached mode comes in.

To cast this spell, we use the `-d` flag with our `docker run` command, telling Docker to send the container off to the background.

```bash
docker run -d busybox:1.36 sleep 1000
```

With a flick of our wands (or rather, the Enter key), the spell is cast, and Docker returns a long string of magical symbols—a container ID. This ID is proof that our BusyBox creature is now running somewhere in the background, quietly counting sheep for 1000 seconds.

But how do we know our creature is truly running, and not just wandering off in the Docker forest? Fear not, young wizard; there is a way to check.

### Casting the `docker ps` Spell

To see the creatures currently roaming the Dockerverse, we use the `docker ps` spell. This spell reveals a list of all the active containers, along with some essential details like their ID, image name, and what they’re currently up to.

```bash
docker ps
```

Behold! There it is our BusyBox container, happily sleeping as commanded. The spell even shows us the short version of our container’s ID, which is the first few characters of the long ID Docker gave us earlier.

But wait, what if you wanted to see all the creatures that have ever existed in your Dockerverse, even the ones that have now perished? For that, we have another spell.

### **Summoning the Ghosts: `docker ps -a`**

The `docker ps -a` spell lets you commune with the ghosts of containers past. These are containers that once roamed your Dockerverse but have since exited, leaving behind only memories and a few logs.

```bash
docker ps -a
```

With this spell, you’ll see a list of all the containers that have ever run on your system, whether they’re still alive or not.

### **The Vanishing Trick: Automatically Removing Containers**

Sometimes, we summon creatures for a quick task, like retrieving a lost scroll, and we don’t want them to linger once the task is done. For this, we have a trick to make them vanish as soon as they’re no longer needed. We simply add the `--rm` flag to our summoning command.

```bash
docker run --rm busybox:1.36 sleep 1
```

In this case, our BusyBox creature wakes up, sleeps for 1 second, and then vanishes into the ether, leaving no trace behind. If you run the **`docker ps -a`** spell afterward, you’ll see that the container is gone completely erased from existence.

### **Naming Your Creatures: The `--name` Flag**

By default, Docker gives your creatures amusing names like “boring\_rosaline” or “kickass\_hopper.” But as a wizard of Docker, you have the power to name your creatures whatever you like. This is done using the `--name` flag when summoning them.

```bash
docker run --name hello_world busybox:1.36
```

Now, when you run the `docker ps -a` spell, you’ll see your BusyBox container proudly bearing the name “hello\_world”. Naming your containers makes it easier to keep track of them, especially when you’re managing an entire menagerie of Docker creatures.

### **The All-Seeing Eye: `docker inspect`**

Finally, we come to one of the most powerful spells in your Docker arsenal: `docker inspect`. This spell allows you to peer into the very soul of a container, revealing all sorts of low-level details that are hidden from the casual observer.

After summoning a new creature in detached mode, like so

```bash
docker run -d busybox:1.36 sleep 1000
```

You can use the `docker inspect` spell to see everything about it,

```bash
docker inspect <container_id>
```

With this spell, you can uncover the container’s IP address, MAC address, image ID, log paths, and much more. It’s like having x-ray vision, allowing you to see every detail about your container.

And so, our journey continues, with new spells and powers at your disposal. You’ve learned how to run containers in the background, name them, and inspect their deepest secrets. As you grow in your mastery of Docker, these tools will become invaluable in managing your containers with the precision and skill of a true Docker wizard.
