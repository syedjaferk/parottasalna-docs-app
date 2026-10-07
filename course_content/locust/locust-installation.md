# Locust Installation

Locust is a powerful and flexible open-source load testing tool that allows you to test the performance of your web applications and APIs. It's written in Python, making it highly customizable and easy to use.&#x20;

In this blog, we’ll guide you through the Locust installation process on different operating systems.

### Prerequisites

Before we begin, ensure the following:

* **Python**: Locust requires Python 3.7 or newer.
* **Pip**: Python's package manager, typically bundled with Python installations.

You can verify your Python and pip versions by running

```bash
python --version
pip --version

```

### Step 1: Install Python (If Not Already Installed)

**For Linux**

* On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3 python3-pip

```

**For Windows**

1. Download Python from [python.org](https://www.python.org/downloads/).
2. Run the installer and check the box **Add Python to PATH**.
3. Complete the installation.

**For macOS**

1. Install Homebrew (if not already installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

2. Install Python using Homebrew:

```bash
brew install python
```

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment helps you manage project dependencies independently

```bash
python -m venv locust-env
source locust-env/bin/activate  # On Windows, use `locust-env\Scripts\activate`
```

### Step 3: Install Locust

With pip, installing Locust is straightforward

```bash
pip install locust
```

Verify the installation by checking the version

```bash
locust --version
```

You should see the installed version of Locust.

### Step 4: Set up a Simple Locust Test

To confirm Locust is working correctly, create a simple test script (save the below script to a locustfile.py),

```python
# locustfile.py
from locust import User, task, between


class MyUser(User):

    wait_time = between(1, 5)

    @task
    def login_url(self):
        print("I am logging in to the url")

```

Run Locust,&#x20;

```bash
locust -f locustfile.py
```

Open your browser and navigate to http://localhost:8089. You’ll see the Locust web interface.
