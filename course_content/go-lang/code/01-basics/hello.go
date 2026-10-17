package main

import "fmt"

func main() {
	fmt.Println("Hello, Go!")
	fmt.Print("no newline here")
	fmt.Print("\n")

	name := "Asha"
	age := 28
	fmt.Printf("Name: %s, Age: %d\n", name, age)
}
