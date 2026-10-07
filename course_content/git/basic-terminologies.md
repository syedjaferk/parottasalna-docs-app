# Basic Terminologies

<mark style="color:orange;">**Repository (Repo)**</mark><mark style="color:orange;">:</mark>&#x20;

A repository is a collection of files and version history managed by Git. It can be local (on your computer) or remote (hosted on a server).

It contains all the files and directories of your project, along with a special hidden directory called `.git`, which stores all the version control information, such as commit history, branches, tags, and configuration settings.

* **Local Repository**: This is the repository stored on your local machine. When you initialize a Git repository in a directory, it becomes a local repository.
* **Remote Repository**: This is a repository hosted on a remote server, typically on a service like GitHub, GitLab, Bitbucket, or a private server. Remote repositories serve as a central location where team members can share and collaborate on code.

<mark style="color:orange;">**Local**</mark>**:** Your Local machine

<mark style="color:orange;">**Commit**</mark>: A commit represents a snapshot of the repository at a specific point in time. It includes changes made to files and a commit message describing the changes.

<mark style="color:orange;">**Branch**</mark>: A branch is a parallel version of the repository. It allows you to work on features or fixes without affecting the main codebase. The default branch is usually called "master" or "main".

<mark style="color:orange;">**Merge**</mark>: Merging combines changes from different branches into one. It's often used to integrate feature branches back into the main branch.

<mark style="color:orange;">**Checkout**</mark>: Checkout switches between different branches or restores files from a specific commit.

<mark style="color:orange;">**Merge Conflict**</mark><mark style="color:orange;">:</mark> A merge conflict occurs when Git cannot automatically merge changes from different branches. It requires manual resolution by the user.

***



<mark style="color:orange;">**Remote**</mark>**:**

In Git, a "remote" refers to a version of the repository that is hosted on a different server or location from your local machine. When you clone a repository, Git automatically creates a remote named "origin" that points to the original repository. However, you can configure multiple remotes if you need to work with multiple repositories.

<mark style="color:orange;">**Pull**</mark>: Pulling is the process of fetching changes from a remote repository and merging them into the local branch.

<mark style="color:orange;">**Push**</mark>: Pushing is the process of sending local commits to a remote repository. It updates the remote repository with your changes.

<mark style="color:orange;">**Clone**</mark>: Cloning creates a copy of a remote repository on your local machine. It allows you to work on the code locally.

<mark style="color:orange;">**Remote**</mark>: A remote is a version of the repository stored on a server, such as GitHub or GitLab. It allows collaboration with others by sharing code.

<mark style="color:orange;">**Fork**</mark>: Forking creates a copy of a repository under your GitHub account. It allows you to freely experiment with changes without affecting the original repository.

<mark style="color:orange;">**Pull Request (PR)**</mark>: A pull request is a request to merge changes from one branch (typically a feature branch) into another (usually the main branch). It's commonly used for code review and collaboration.
