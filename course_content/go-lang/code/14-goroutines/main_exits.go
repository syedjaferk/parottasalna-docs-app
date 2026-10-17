package main

import "fmt"

func main() {
	go fmt.Println("hello from a goroutine")
	fmt.Println("main is done")
	// main returns here; the goroutine usually never gets to print
}
