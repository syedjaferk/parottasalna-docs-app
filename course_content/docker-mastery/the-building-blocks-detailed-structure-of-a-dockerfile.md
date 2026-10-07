# The Building Blocks – Detailed Structure of a Dockerfile


<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/uP_-l3sKwYo" title="YouTube video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>


Alex now knows the basics, but it’s time to get their hands dirty by writing an actual Dockerfile. Below is the Dockerfile for a flask application. (for now just ignore app.py)

```docker
# Use an official Python runtime as a parent image
FROM python:3.9-slim
 
# Set the working directory in the container
WORKDIR /app
 
# Copy the current directory contents into the container at /app
COPY . /app
 
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
 
# Make port 80 available to the world outside this container
EXPOSE 80
 
# Define environment variable
ENV NAME World
 
# Run app.py when the container launches
CMD ["python", "app.py"]
```

### **The `FROM` Instruction: Choosing the Foundation**

The first thing Alex learns is the `FROM` instruction, which sets the base image for their container. It’s like choosing the foundation for a house.

* **Purpose:**
  * The `FROM` instruction initializes a new build stage and sets the Base Image for subsequent instructions.
* **Choosing a Base Image:**
  * Alex decides to use a Python base image for their application. They learn that `python:3.9-slim` is a lightweight version, saving space and reducing the size of the final image.

```docker
FROM python:3.9-slim
```

> **Story Note**: Think of `FROM` as picking the type of bread for your sandwich. Do you want white, whole wheat, or maybe something gluten-free? Your choice sets the tone for the rest of the recipe.

### **The `LABEL` Instruction: Adding Metadata (Optional)**

Next, Alex discovers the `LABEL` instruction. While optional, it’s a good practice to include metadata about the image.

* **Purpose:**
  * The `LABEL` instruction adds metadata like version, description, or maintainer information to the image.
* **Example:**
  * Alex decides to add a maintainer label

```docker
LABEL maintainer="alex@example.com"
```

> **Story Note**: This is like writing your name on a sandwich wrapper, so everyone knows who made it and what’s inside.

### **The `RUN` Instruction: Building the Layers**

The `RUN` instruction is where Alex can execute commands inside the image, such as installing dependencies.

* **Purpose:**
  * The `RUN` instruction runs any commands in a new layer on top of the current image and commits the results.
* **Example:**
  * To install the Flask framework, Alex writes

```docker
RUN pip install flask
```

> **Story Note**: Imagine slicing tomatoes and cheese for your sandwich and placing them carefully on top. Each ingredient (command) adds a layer of flavor.

### **The `COPY` and `ADD` Instructions: Bringing in Ingredients**

Now, Alex needs to bring their application code into the container, which is where the `COPY` and `ADD` instructions come into play.

* **COPY:**
  * The `COPY` instruction copies files or directories from the host filesystem into the container’s filesystem.
* **ADD:**
  * The `ADD` instruction is similar to `COPY` but with additional features, like extracting compressed files.
* **Example:**
  * Alex copies their application code into the container:

```docker
COPY . /app
```

> _Story Note_: This is like moving ingredients from your fridge (host) to the counter (container) where you’re preparing the sandwich.

### **The `WORKDIR` Instruction: Setting the Workspace**

Alex learns that setting a working directory makes it easier to manage paths within the container.

* **Purpose:**
  * The `WORKDIR` instruction sets the working directory for subsequent instructions.
* **Example:**
  * Alex sets the working directory to `/app`:

```docker
WORKDIR /app
```

> _Story Note_: This is like setting up a designated area on your counter where you’ll assemble your sandwich—keeping everything organized.

### **The `CMD` and `ENTRYPOINT` Instructions: The Final Touch**

Finally, Alex learns how to define the default command that will run when the container starts.

* **CMD:**
  * Provides defaults for an executing container, but can be overridden.
* **ENTRYPOINT:**
  * Configures a container that will run as an executable, making it difficult to override.
* **Example:**
  * Alex uses `CMD` to specify the command to start their Flask app:

```docker
CMD ["python", "app.py"]
```

> _Story Note_: Think of `CMD` as the final step in making your sandwich—like deciding to add a toothpick to hold everything together before serving.

### Breakdown of the Dockerfile:

1. **FROM python:3.9-slim**:
   * This line specifies the base image. In this case, it uses a slim version of Python 3.9, which is lightweight and sufficient for a simple Flask application.
2. **WORKDIR /app**:
   * This sets the working directory inside the container to `/app`. All subsequent commands will be run inside this directory.
3. **COPY . /app**:
   * This copies everything from your current directory on the host machine into the `/app` directory inside the container.
4. **RUN pip install –no-cache-dir -r requirements.txt**:
   * This installs the necessary Python packages listed in the `requirements.txt` file. The `--no-cache-dir` option reduces the image size by not caching the downloaded packages.
5. **EXPOSE 80**:
   * This makes port 80 available for external access. It’s where the Flask application will listen for incoming requests.
6. **ENV NAME World**:
   * This sets an environment variable `NAME` to “World”. You can access this variable in your Python code.
7.  **CMD \[“python”, “app.py”]**:

    * This tells the container to run the `app.py` file using Python when it starts.



### Example Flask Application (`app.py`):

To complete the example, here’s a simple Flask application you can use,

```python
from flask import Flask
import os
 
app = Flask(__name__)
 
@app.route('/')
def hello():
    name = os.getenv('NAME', 'World')
    return f'Hello, {name}!'
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
```

#### Example `requirements.txt`:

And here’s the `requirements.txt` file listing the dependencies for the Flask app,

```
Flask==2.0.3
```

### Building and Running the Docker Image:

* Build the Docker image using the Dockerfile

```docker
docker build -t my-flask-app .
```

* Run the Docker container

```bash
docker run -p 4000:80 my-flask-app
```

* This maps port 4000 on your host machine to port 80 in the container.

Open your browser and go to `http://localhost:4000`, and you should see “Hello, World!” displayed on the page.

You can customize the `ENV NAME` in the Dockerfile or by passing it as an argument when running the container.

```bash
docker run -p 4000:80 -e NAME=Alex my-flask-app
```

This will display “Hello, Alex!” instead.
