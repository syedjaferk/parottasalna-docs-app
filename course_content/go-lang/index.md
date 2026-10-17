# 40 Days of Go

Go (also called Golang) is a small, fast language for servers, command-line tools and anything that
needs to do many things at once. This course follows the **40 Days of Go** journey from the
[syedjaferk/40_days_of_go_lang](https://github.com/syedjaferk/40_days_of_go_lang) repository: start with
the basics, build file and command-line tools, then web APIs and a database, and finish with
goroutines, channels and tests.

:::{note}
**Why learn Go, in one line?** You write simple code, the compiler checks it hard, and you ship one
fast program with nothing else to install. Docker, Kubernetes and Terraform are all written in Go.
:::

```{raw} html
:file: diagrams/course-map.html
```

## How each session works

1. **The big idea**: the topic in plain words, with an everyday example.
2. **A picture**: a diagram of the idea.
3. **Runnable code**: every program is run for real, and the output you see is what it printed.
4. **Common mistakes**: what trips beginners up.
5. **Hands-on exercises**: try first, then reveal the solution (every solution was run too).
6. **Practice**: a quiz and a flashcard deck for the session.

:::{tip}
New here? Start with **[Setup](setup.md)**, then go in order. Type the examples yourself rather than
copying; your fingers learn the syntax faster than your eyes do.
:::

:::{important}
**Read the compiler's errors.** Go's messages are short and exact (`declared and not used`,
`missing return`). Fix the first one, run again, and repeat. That loop is the fastest way to learn.
:::

```{toctree}
:maxdepth: 1
:caption: Getting started

setup
```

```{toctree}
:maxdepth: 1
:caption: Phase 1 · Foundations

sessions/01-hello-go-basics
sessions/02-functions
sessions/03-arrays-slices
sessions/04-maps
sessions/05-structs-json
sessions/06-pointers
sessions/07-errors
```

```{toctree}
:maxdepth: 1
:caption: Phase 2 · Files and command-line tools

sessions/08-files
sessions/09-command-line
sessions/10-logging-config
```

```{toctree}
:maxdepth: 1
:caption: Phase 3 · Web and data

sessions/11-http
sessions/12-todo-api
sessions/13-database
```

```{toctree}
:maxdepth: 1
:caption: Phase 4 · Concurrency and testing

sessions/14-goroutines
sessions/15-waitgroup
sessions/16-mutex
sessions/17-channels
sessions/18-testing
```
