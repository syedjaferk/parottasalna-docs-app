package main

import "fmt"

type User struct{ Name string }

func greet(u *User) string {
	if u == nil {
		return "hello, stranger"
	}
	return "hello, " + u.Name
}

func main() {
	fmt.Println(greet(&User{"Asha"}))
	fmt.Println(greet(nil))

	defer func() { fmt.Println("recovered:", recover()) }()
	var u *User
	fmt.Println(u.Name) // nil pointer dereference
}
