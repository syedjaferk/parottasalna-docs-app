package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
)

// ---- models ----
type Todo struct {
	ID        int    `json:"id"`
	Title     string `json:"title"`
	Completed bool   `json:"completed"`
}

type CreateTodoRequest struct {
	Title string `json:"title"`
}

// ---- storage (in memory, safe for many requests at once) ----
type Store struct {
	mu     sync.Mutex
	todos  []Todo
	nextID int
}

func NewStore() *Store { return &Store{nextID: 1, todos: []Todo{}} }

func (s *Store) List() []Todo {
	s.mu.Lock()
	defer s.mu.Unlock()
	return append([]Todo{}, s.todos...)
}

func (s *Store) Add(title string) Todo {
	s.mu.Lock()
	defer s.mu.Unlock()
	t := Todo{ID: s.nextID, Title: title}
	s.nextID++
	s.todos = append(s.todos, t)
	return t
}

// ---- handlers ----
type API struct{ store *Store }

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}

func (a *API) Home(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"message": "Welcome to the TODO api"})
}

func (a *API) Todos(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		writeJSON(w, http.StatusOK, a.store.List())
	case http.MethodPost:
		var req CreateTodoRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Title == "" {
			http.Error(w, "title is required", http.StatusBadRequest)
			return
		}
		writeJSON(w, http.StatusCreated, a.store.Add(req.Title))
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

// ---- try it ----
func do(srv *httptest.Server, method, path, body string) {
	req, _ := http.NewRequest(method, srv.URL+path, strings.NewReader(body))
	resp, _ := http.DefaultClient.Do(req)
	defer resp.Body.Close()
	text, _ := io.ReadAll(resp.Body)
	fmt.Printf("%-5s %-7s %d %s", method, path, resp.StatusCode, text)
}

func main() {
	api := &API{store: NewStore()}
	mux := http.NewServeMux()
	mux.HandleFunc("/", api.Home)
	mux.HandleFunc("/todos", api.Todos)
	srv := httptest.NewServer(mux)
	defer srv.Close()

	do(srv, "GET", "/", "")
	do(srv, "GET", "/todos", "")
	do(srv, "POST", "/todos", `{"title":"Learn Go"}`)
	do(srv, "POST", "/todos", `{"title":"Build an API"}`)
	do(srv, "POST", "/todos", `{}`)
	do(srv, "GET", "/todos", "")
	do(srv, "GET", "/nope", "")
}
