# Setup: install Go and run your first program

You need three things: Go itself, a folder to work in, and a text editor (VS Code with the official
**Go** extension works well).

## 1. Install Go

Download the installer for your system from [go.dev/dl](https://go.dev/dl/) and follow the steps, then
open a **new** terminal and check:

```bash
go version
```

You should see something like this (this course was written and every example run with Go 1.27;
anything from Go 1.22 onward behaves the same):

```text
go version go1.27.2 linux/amd64
```

## 2. Make a project folder

```bash
mkdir hello-go
cd hello-go
go mod init hello-go
```

`go mod init` creates a small file called `go.mod`. It names your **module** (your project) and lists
the third-party packages you use. You do this once per project.

## 3. Write and run

Create `main.go` with the program from Session 1, then:

```bash
go run main.go      # build + run + clean up
go build            # produce an executable file named after the module
go fmt ./...        # format all code the standard way
go vet ./...        # catch suspicious code
```

## The course code

Every example in this course is a plain `.go` file in a folder per session. Each is run on its own with
`go run file.go`, because several small programs share a folder and each has its own `main`.
The output you see on the pages was captured by running the files, not typed by hand.

:::{note}
Sessions 10 and 13 use outside packages (`yaml`, `logrus`, `sqlite`). Inside a module, run
`go get <package>` once, or `go mod tidy`, and Go downloads them.
:::

## How this course follows the 40 Days of Go repository

The original repository has working code for 13 topics. This course turns each into a session and fills in
the topics the syllabus names but the repository does not yet cover:

| Repository folder | Session |
|---|---|
| `01.basics` | 1 Hello & basics, 2 Functions, 3 Arrays & slices, 4 Maps |
| `02.structs` | 5 Structs & JSON |
| `03.pointers` | 6 Pointers |
| (syllabus: error handling, retry logic) | 7 Errors |
| `04.files` | 8 Files |
| `05.command_line`, `06.file_finder` | 9 Command line |
| `07.logging` | 10 Logging & config |
| `08.http` | 11 HTTP |
| `09.todo-api` | 12 Todo API |
| `10.todo_db` | 13 Database |
| `11.gortn` | 14 Goroutines |
| `12.waitgrp` | 15 WaitGroup |
| `13.mutx` | 16 Mutex |
| (syllabus: goroutines & channels) | 17 Channels & select |
| (testing) | 18 Testing |
