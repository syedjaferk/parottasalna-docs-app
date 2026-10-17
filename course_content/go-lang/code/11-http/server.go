package main

import (
	"encoding/json"
	"fmt"
	"net/http"
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

func main() {
	http.HandleFunc("/", home)
	http.HandleFunc("/users", users)

	fmt.Println("listening on :8081")
	if err := http.ListenAndServe(":8081", nil); err != nil {
		fmt.Println("error:", err)
	}
}
