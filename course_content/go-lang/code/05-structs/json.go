package main

import (
	"encoding/json"
	"fmt"
)

type Geo struct {
	Lat float64 `json:"lat"`
	Lng float64 `json:"lng"`
}

type User struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email,omitempty"`
	Geo   Geo    `json:"geo"`
	token string // lowercase: private, never in JSON
}

func main() {
	data := `{"id": 1, "name": "Syed", "geo": {"lat": 12.45, "lng": 80.56}}`

	var u User
	if err := json.Unmarshal([]byte(data), &u); err != nil {
		fmt.Println("bad json:", err)
		return
	}
	fmt.Printf("%+v\n", u)

	u.Email = "syed@example.com"
	u.token = "secret"
	out, _ := json.Marshal(u)
	fmt.Println(string(out))

	pretty, _ := json.MarshalIndent(Geo{1.5, 2.5}, "", "  ")
	fmt.Println(string(pretty))

	err := json.Unmarshal([]byte(`{"id": "one"}`), &u)
	fmt.Println(err)
}
