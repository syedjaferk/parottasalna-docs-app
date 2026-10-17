package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
)

type User struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

func home(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello from Go!")
}

func users(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		fmt.Fprintln(w, "Get request received")
	case http.MethodPost:
		var u User
		if err := json.NewDecoder(r.Body).Decode(&u); err != nil {
			http.Error(w, "Invalid JSON", http.StatusBadRequest)
			return
		}
		fmt.Fprintln(w, "Post request received:", u.Name, u.Age)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func call(srv *httptest.Server, method, path, body string) {
	req, _ := http.NewRequest(method, srv.URL+path, strings.NewReader(body))
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer resp.Body.Close()
	text, _ := io.ReadAll(resp.Body)
	fmt.Printf("%-6s %-7s -> %d %s", method, path, resp.StatusCode, text)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", home)
	mux.HandleFunc("/users", users)

	srv := httptest.NewServer(mux) // a real server on a random local port
	defer srv.Close()

	call(srv, "GET", "/", "")
	call(srv, "GET", "/users", "")
	call(srv, "POST", "/users", `{"name":"Asha","age":30}`)
	call(srv, "POST", "/users", `not json`)
	call(srv, "DELETE", "/users", "")
}
