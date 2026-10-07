# Running Locust in Distributed Mode with Master and Workers

When load testing large-scale systems, a single machine may not provide enough computational power to simulate thousands or millions of users. Locust, a powerful load testing framework, supports distributed testing by allowing you to run a master-worker setup. This setup splits the workload across multiple machines, enabling the simulation of a massive number of users.

In this blog, we’ll explore how to set up and run Locust in distributed mode using a **master** and multiple **workers** (formerly known as slaves).

### Why Distributed Testing?

Distributed testing is beneficial when:

* You need to simulate a very high number of users.
* A single machine cannot handle the computational load.
* You want to utilize the power of multiple machines to increase test efficiency.

### Locust Distributed Architecture

1. **Master Node**:
   * Manages the test, aggregates statistics, and distributes tasks to worker nodes.
   * Runs the web UI for test control and monitoring.
2. **Worker Nodes**:
   * Execute the load generation tasks as instructed by the master.
   * Report results back to the master node.

###

### Setting Up Locust in Distributed Mode

### Step 1: Prepare Your Locust Script

Create a Locust test script (e.g., `locustfile.py`) with tasks for the load test. Here’s a simple example.

```python
from locust import HttpUser, task, constant  


class MyTestUser(HttpUser):  
    wait_time = constant(1)  
    host = "http://localhost:8000"  

    @task  
    def get_index(self):  
        self.client.get("/")  

```

Place this script on all machines (master and workers).

### Step 2: Start the Master Node

Run the following command on the **master** machine

```bash
locust -f locustfile.py --master  
```

This starts the master node, which listens for incoming connections from worker nodes. By default, the master listens on port `5557` for worker connections and port `5558` for results.

You can also specify the host interface (e.g., `0.0.0.0` to bind to all interfaces)

```bash
locust -f locustfile.py --master --master-bind-host=0.0.0.0  
```

### Step 3: Start the Worker Nodes

Run the following command on each **worker** machine

```bash
locust -f locustfile.py --worker --master-host=<MASTER_IP>  
```

Replace `<MASTER_IP>` with the IP address of the master node.

For example:

```bash
locust -f locustfile.py --worker --master-host=192.168.1.10  
```

### Step 4: Control the Test

* Open the Locust web interface by navigating to `http://<MASTER_IP>:8089` in your browser.
* Set the number of users and spawn rate in the web UI.
* Start the test and monitor the aggregated results in real-time.

### Key Parameters

#### Master-Specific Options

* `--master`: Enables master mode.
* `--master-bind-host`: Sets the IP address or hostname for the master to bind to. Default: `127.0.0.1`.
* `--master-bind-port`: Sets the port for workers to connect. Default: `5557`.

#### Worker-Specific Options

* `--worker`: Enables worker mode.
* `--master-host`: Specifies the IP address or hostname of the master. Default: `127.0.0.1`.

### Scaling the Test

To scale your test, simply add more worker nodes. Each worker contributes its computational resources to simulate additional users.

For example, if each worker can handle 1,000 users and you add 5 workers, you can simulate 5,000 users collectively.

### Example: Running on Docker

Locust’s distributed setup can also be easily run using Docker.

#### Docker-Compose Example

Create a `docker-compose.yml` file

```yaml
version: '3.8'  

services:  
  master:  
    image: locustio/locust  
    command: >  
      locust -f /mnt/locustfile.py --master  
    ports:  
      - "8089:8089"  
    volumes:  
      - ./locustfile.py:/mnt/locustfile.py  

  worker:  
    image: locustio/locust  
    command: >  
      locust -f /mnt/locustfile.py --worker --master-host=master  
    depends_on:  
      - master  
    volumes:  
      - ./locustfile.py:/mnt/locustfile.py  
    scale: 5  

```

Run the following command to start the distributed setup

```bash
docker-compose up --scale worker=5  
```

This creates 1 master node and 5 worker nodes using Docker containers.

### Monitoring Distributed Tests

* The web UI aggregates statistics from all workers.
* You can track the total number of requests, failures, and response times in real time.
* Logs from each worker provide detailed insights for debugging.

### Tips for Distributed Locust

1. **Match Capacity**: Ensure each worker machine has sufficient resources (CPU, memory, and network bandwidth) to handle the load.
2. **Sync Scripts**: Keep the `locustfile.py` script consistent across all nodes.
3. **Use Networking Best Practices**: Use fast and reliable networks to minimize latency between master and workers.
