package main

import "fmt"

type User struct{ Name string }

func renameCopy(u User)     { u.Name = "Changed" }
func renameOriginal(u *User) { u.Name = "Changed" } // same as (*u).Name

func doubleCopy(n int)     { n = n * 2 }
func doubleOriginal(n *int) { *n = *n * 2 }

func main() {
	n := 5
	doubleCopy(n)
	fmt.Println(n)
	doubleOriginal(&n)
	fmt.Println(n)

	u := User{Name: "Syed"}
	renameCopy(u)
	fmt.Println(u.Name)
	renameOriginal(&u)
	fmt.Println(u.Name)

	// new gives a pointer to a zero value
	q := new(int)
	*q = 7
	fmt.Println(*q)
}
