package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"time"
)

type Post struct {
	ID    int    `json:"id"`
	Title string `json:"title"`
}

func main() {
	// a stand-in for a real API such as jsonplaceholder.typicode.com
	api := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(Post{ID: 1, Title: "hello"})
	}))
	defer api.Close()

	// always set a timeout: the default client waits forever
	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(api.URL + "/posts/1")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer resp.Body.Close()

	fmt.Println(resp.Status, resp.Header.Get("Content-Type"))
	var p Post
	if err := json.NewDecoder(resp.Body).Decode(&p); err != nil {
		fmt.Println(err)
		return
	}
	fmt.Printf("%+v\n", p)
}
