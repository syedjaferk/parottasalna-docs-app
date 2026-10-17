# Session 10 · Logging and configuration

## The big idea

When a program runs on a server nobody is watching it. **Logs** are its diary: what happened, when,
and how serious. **Configuration** is its settings: things you want to change (a port, a minimum
age, a log level) without editing and rebuilding the code. Together they make a program you can
operate.

**Everyday example:** a ship. The captain's log records events with their importance ("storm
warning", "engine failure"). The ship's settings (speed limit, course) come from the instruction
sheet, not from rebuilding the ship.

:::{admonition} In plain words
:class: tip
Use the standard `log` package for quick messages, or `log/slog` for **structured** logs with
levels and key=value fields. Put settings in a YAML file, read it into a struct once at start-up.

**Reach for it when:**

- the program runs unattended and you need to find out what went wrong
- different machines need different settings
- you want logs a tool can search (JSON)
:::

```{raw} html
:file: ../diagrams/log-levels.html
```

## Standard logging with `log` and `slog`

`main.go`: the output below has timestamps removed so it is repeatable; real logs include the time.

```{literalinclude} ../code/10-logging/main.go
:language: go
```

```{literalinclude} ../code/10-logging/main.out
:language: text
```

- `log.Println` writes to **stderr** with a timestamp (we turned it off). `log.Fatal` also exits.
- `slog` takes a message plus alternating keys and values: `"user", "Syed"`.
- Levels: Debug < Info < Warn < Error. The default handler hides Debug.
- Switch between human-friendly `TextHandler` and machine-friendly `JSONHandler` without changing the log calls.
- `With("app", "todo")` stamps every later line with those fields.

## The course's logging library: logrus

The repository uses the third-party `logrus` package. It works the same idea: levels and fields, with
a JSON formatter. Add it with `go get github.com/sirupsen/logrus`.

`logrus.go`

```{literalinclude} ../code/10-logging/logrus.go
:language: go
```

```{literalinclude} ../code/10-logging/logrus.out
:language: text
```

Newer projects often prefer `slog` because it ships with Go; logrus is still everywhere in existing code.

## Reading a YAML config

`config.yaml`

```{literalinclude} ../code/10-logging/config.yaml
:language: yaml
```

`config.go` reads the file into a struct using `gopkg.in/yaml.v3` (`go get gopkg.in/yaml.v3`).

```{literalinclude} ../code/10-logging/config.go
:language: go
```

```{literalinclude} ../code/10-logging/config.out
:language: text
```

The `yaml:"min_age"` tags work exactly like the JSON ones from Session 5. Return the config and
an error; let `main` decide how to react to a missing or broken file.

:::{note}
Third-party packages come from a `go.mod` file. `go mod init myapp` creates it, `go get` adds a
package, and `go mod tidy` cleans up. The course code folder has a ready `go.mod`.
:::

## Common mistakes

- **Logging secrets.** Never log passwords, tokens or full card numbers.
- **Logging in a loop at Info level.** Millions of lines hide the one that matters.
- **Unstructured messages** like `"user "+name+" failed"`. Use fields so you can search by `user`.
- **Hard-coding settings** (ports, database passwords) in source. Read them from config or environment variables.
- **Not handling a missing config.** Check the error and say which file failed.

## Hands-on exercises

**Exercise 1 · Leveled output.** Create a text `slog` logger writing to stdout at `Warn` level and log one Info and one Warn message. Only the Warn should show (drop the time attribute to keep it repeatable).

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"log/slog"
	"os"
)

func main() {
	logger := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelWarn,
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if a.Key == slog.TimeKey {
				return slog.Attr{}
			}
			return a
		},
	}))
	logger.Info("starting")
	logger.Warn("disk almost full", "percent", 91)
}
```

```text
level=WARN msg="disk almost full" percent=91
```

</details>

**Exercise 2 · Parse inline YAML.** Unmarshal the text `port: 8081\nhost: localhost` into a struct and print the address `localhost:8081`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"

	"gopkg.in/yaml.v3"
)

type Server struct {
	Host string `yaml:"host"`
	Port int    `yaml:"port"`
}

func main() {
	var s Server
	if err := yaml.Unmarshal([]byte("port: 8081\nhost: localhost"), &s); err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("%s:%d\n", s.Host, s.Port)
}
```

```text
localhost:8081
```

</details>

**Exercise 3 · Environment override.** Read `APP_PORT` from the environment, and fall back to `"8081"` when it is not set.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"os"
)

func getenv(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok {
		return v
	}
	return fallback
}

func main() {
	fmt.Println(getenv("APP_PORT_DEMO", "8081"))
}
```

```text
8081
```

`os.LookupEnv` tells "unset" apart from "set to empty".

</details>
