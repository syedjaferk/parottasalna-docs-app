# Session 11 · HTTP servers and clients

## Watch the class

```{raw} html
<iframe style="width:100%; aspect-ratio:16/9; border:0; border-radius:12px"
  src="https://www.youtube-nocookie.com/embed/uXRqtFXFkLE"
  title="Day 14 | Learn Go from Scratch | Call REST APIs using GET and POST in Go" loading="lazy" allowfullscreen
  allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>
```

## The big idea

The web runs on **HTTP**: a client sends a *request* ("GET /users"), a server sends back a
*response* (a status code and some data). Go ships a production-grade HTTP server in its standard
library, so a working web service is about twenty lines with no framework.

**Everyday example:** a restaurant. The customer (client) gives an order slip (request) with a
dish name and details. The waiter (the router) hands it to the right cook (a handler), and the
plate comes back with a note: "served" (200), "we don't have that" (404) or "you ordered it wrong" (400).

:::{admonition} In plain words
:class: tip
A **handler** is a function `func(w http.ResponseWriter, r *http.Request)`. Register it for a path
with `http.HandleFunc`, then call `http.ListenAndServe(":8081", nil)`. Read the request from `r`,
write the answer to `w`.

**Reach for it when:**

- you want to expose your program's data or actions over the network
- you call another service's API (use `http.Client`)
- you need a quick webhook or health-check endpoint
:::

```{raw} html
:file: ../diagrams/http-flow.html
```

## A first server

`server.go`: this is the course's server, tidied up.

```{literalinclude} ../code/11-http/server.go
:language: go
```

Start it with `go run server.go`, then in another terminal:

```bash
curl localhost:8081/
curl -X POST -d '{"name":"Asha","age":30}' localhost:8081/users
curl -i -X PUT localhost:8081/users
```

What I saw when I ran exactly these commands:

```text
listening on :8081
Hello from Go!
Post request received: Asha 30
HTTP/1.1 405 Method Not Allowed
```

(The first line is the server's own message; the rest is what `curl` printed.)

- `fmt.Fprintln(w, ...)` writes into the response body.
- `switch r.Method` lets one path behave differently for GET and POST.
- `json.NewDecoder(r.Body).Decode(&u)` reads a JSON request body into a struct.
- `http.Error(w, message, code)` sets the status and a plain-text message.
- The first matching handler with the longest path wins; `"/"` is the catch-all.

## Trying the server without a terminal

`try_server.go` contains the same handlers but starts them with `httptest.NewServer`, which listens
on a random free port and lets us send real requests from inside the program. This is also how you
test handlers (Session 18).

```{literalinclude} ../code/11-http/try_server.go
:language: go
```

```{literalinclude} ../code/11-http/try_server.out
:language: text
```

Note the status codes: bad JSON gives `400`, a method we do not handle gives `405`.

## Calling an API

`client.go` is a client. A tiny local server stands in for a public API so the example is
repeatable offline; against a real one you would only change the URL.

```{literalinclude} ../code/11-http/client.go
:language: go
```

```{literalinclude} ../code/11-http/client.out
:language: text
```

- **Always set a timeout** on your client. `http.Get` uses a default client that waits forever.
- `defer resp.Body.Close()` after checking the error, every time.
- Check `resp.StatusCode` too: a 404 is a *successful call* with an unhappy answer, not an `err`.

## Common mistakes

- **Writing the status after the body.** `w.WriteHeader(201)` must come before the first write.
- **Forgetting `return` after `http.Error`.** The handler keeps running and writes more.
- **Not closing `resp.Body`.** Leaks connections.
- **No timeout on clients or servers.** One slow peer can hang your program.
- **Trusting the request.** Validate every field; never build SQL or file paths from raw input.
- **Port already in use.** `listen tcp :8081: bind: address already in use` means another process holds the port.

## Hands-on exercises

**Exercise 1 · Health check.** Add a handler for `/health` returning `ok`. Test it with `httptest.NewRecorder`, which captures a response without a network.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
)

func health(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "ok")
}

func main() {
	rec := httptest.NewRecorder()
	req := httptest.NewRequest("GET", "/health", nil)
	health(rec, req)
	fmt.Println(rec.Code, rec.Body.String())
}
```

```text
200 ok
```

</details>

**Exercise 2 · Greeting by query.** Handler for `/hello?name=Asha` that answers `Hello, Asha!` and uses `World` when `name` is missing.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"fmt"
	"net/http"
	"net/http/httptest"
)

func hello(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	if name == "" {
		name = "World"
	}
	fmt.Fprintf(w, "Hello, %s!", name)
}

func main() {
	for _, url := range []string{"/hello?name=Asha", "/hello"} {
		rec := httptest.NewRecorder()
		hello(rec, httptest.NewRequest("GET", url, nil))
		fmt.Println(rec.Body.String())
	}
}
```

```text
Hello, Asha!
Hello, World!
```

</details>

**Exercise 3 · JSON response.** Return `{"status":"up","version":"1.0"}` with the header `Content-Type: application/json`.

<details class="solution"><summary>Solution</summary>

```go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
)

func status(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "up", "version": "1.0"})
}

func main() {
	rec := httptest.NewRecorder()
	status(rec, httptest.NewRequest("GET", "/status", nil))
	fmt.Println(rec.Header().Get("Content-Type"))
	fmt.Print(rec.Body.String())
}
```

```text
application/json
{"status":"up","version":"1.0"}
```

Set headers **before** writing the body.

</details>
