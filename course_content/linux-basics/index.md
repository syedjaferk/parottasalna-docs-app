# Linux Basics: The Commands Every Beginner Needs

Linux runs most of the internet: web servers, phones (Android), cloud machines, routers, supercomputers and the
servers behind almost every app you use. If you want to work in software, data, DevOps or cloud, **you will
meet Linux**, and the first thing you meet is the **terminal**.

This course takes you from *"what is a terminal?"* to *"I can find files, fix permissions, read logs, manage
processes and write my own scripts"*. You learn by **doing**: every session has commands to run, the exact output
you should see, a **practice folder** with sample files, and **tryouts** that a small checker script marks for you.

:::{note}
**You do not need to know anything about Linux or programming.** You need a computer and curiosity. Mistakes are
part of learning, and the practice folder is a safe sandbox where you *can't* hurt anything important.
:::

## What you will be able to do

```{raw} html
:file: diagrams/l00-journey.html
```

| After this course you can... | Sessions |
|---|---|
| Open a terminal, run commands and read their help | 1 |
| Move around the file system with confidence | 2 |
| Create, copy, move and delete files and folders safely | 3 |
| Read, search through and edit text files | 4 |
| Combine commands with pipes to answer real questions about data and logs | 5 |
| Find files and text anywhere on the system | 6 |
| Understand users, groups and permissions (`rwx`, `chmod`, `sudo`) | 7 |
| See and control running programs (processes, services, scheduled jobs) | 8 |
| Install software, download files, compress archives, check the network | 9 |
| Write shell scripts that automate your work | 10 |
| Diagnose disk, memory and log problems like an admin | 11 |

## How each session works

1. **The big idea** with an everyday comparison.
2. **Try it**: commands to type in your practice folder, with the real output shown.
3. **What just happened?** The command explained piece by piece, in plain words.
4. **Common mistakes** and what the error messages mean.
5. **Tryouts**: three small jobs (and a checker: `bash check.sh <session>`). Answers are hidden so you try first.
6. **Quiz** at the end of each session, and a **timed final exam** for the whole course.

:::{tip}
**Type every command yourself.** Copy-paste teaches your clipboard, not your fingers. Even when it feels slow, typing is
how commands stick.
:::

## Before you begin

Do the **[Setup](setup.md)** first (15 minutes). You'll get a Linux terminal (on Windows, macOS or Linux), and create the
`~/linux-lab` practice folder with one command.

```{toctree}
:maxdepth: 1
:caption: Start here

setup
cheatsheet
```

```{toctree}
:maxdepth: 1
:caption: Part 1 · Getting around

sessions/01-first-steps
sessions/02-files-and-directories
sessions/03-working-with-files
sessions/04-reading-and-editing
```

```{toctree}
:maxdepth: 1
:caption: Part 2 · Working with text and finding things

sessions/05-pipes-and-text
sessions/06-finding-things
```

```{toctree}
:maxdepth: 1
:caption: Part 3 · Running a system

sessions/07-users-and-permissions
sessions/08-processes-and-services
sessions/09-packages-and-network
```

```{toctree}
:maxdepth: 1
:caption: Part 4 · Automating and fixing

sessions/10-shell-scripting
sessions/11-troubleshooting
```
