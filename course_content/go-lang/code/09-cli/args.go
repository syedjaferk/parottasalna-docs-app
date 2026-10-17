package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Println(len(os.Args) > 0) // Args[0] is the program itself
	if len(os.Args) < 2 {
		fmt.Println("Usage: app <name>")
		return
	}
	fmt.Println("Hello", os.Args[1])
}
