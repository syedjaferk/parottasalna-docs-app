# Q1 - Initialize a Repository and Basic Configurations

### Problem Statement

* **Initialize a Repository**\
  Create a new Git repository in a folder named `MyProject`. This initializes a `.git` folder where Git will track changes. Verify the repository is initialized using `git status`.
* **Set Up User Details Globally**\
  Configure your Git setup by setting your global username as `DevUser` and email as `devuser@example.com`. This ensures all commits made by you are attributed correctly across all repositories.
* **Set Up Project-Specific User Details**\
  Override the global Git configuration for a specific project. Set `ProjectUser` as the username and `projectuser@example.com` as the email to track contributions differently in that project.
* **Check Configuration**\
  Display all Git configuration details to ensure setup correctness. Use `git config --list` and filter only the `user` settings for clarity.

### Solution

#### **1. Initialize a Repository**

1. Open a terminal and navigate to the folder where you want to create the repository

```bash
mkdir MyProject
cd MyProject
```

2. Initialize the Git repository

```bash
git init
```

This creates a `.git` folder in the `MyProject` directory.

3. Verify that the repository is initialized

```bash
git status
```

You should see a message like,

```bash
On branch main
No commits yet
nothing to commit, working tree clean
```

**2. Set Up User Details Globally**

1. Set global username  and email

```bash
git config --global user.name "Syed Jafer"
git config --global user.email "contact.syedjafer@gmail.com"
```

2. Verify the global configuration is updated

```bash
git config --global --list
```


![](/_assets/image.png)
