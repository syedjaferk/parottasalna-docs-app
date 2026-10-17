package main

import (
	"fmt"
	"os"
)

func main() {
	file, err := os.Create("sample.txt")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close() // always close what you open

	n, _ := file.WriteString("Hello from Go\n")
	fmt.Println("wrote", n, "bytes")

	// the one-liner for small files: replaces the whole file
	err = os.WriteFile("notes.txt", []byte("line one\nline two\n"), 0644)
	fmt.Println("WriteFile error:", err)
}
