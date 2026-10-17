package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	os.WriteFile("notes.txt", []byte("line one\nline two\n"), 0644)

	data, err := os.ReadFile("notes.txt")
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(data[:4])         // raw bytes
	fmt.Print(string(data))       // as text

	// append: open with flags instead of overwriting
	f, err := os.OpenFile("notes.txt", os.O_APPEND|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println(err)
		return
	}
	f.WriteString("line three\n")
	f.Close()

	// read line by line, good for big files
	f, _ = os.Open("notes.txt")
	defer f.Close()
	scanner := bufio.NewScanner(f)
	for i := 1; scanner.Scan(); i++ {
		fmt.Printf("%d: %s\n", i, scanner.Text())
	}

	_, err = os.ReadFile("missing.txt")
	fmt.Println(err)
	fmt.Println(os.IsNotExist(err))
}
