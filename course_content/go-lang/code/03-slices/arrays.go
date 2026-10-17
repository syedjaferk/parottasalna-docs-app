package main

import "fmt"

func main() {
	var grades [5]int
	grades[0] = 95
	colors := [...]string{"Red", "Green", "Blue"}

	fmt.Println(grades, len(grades))
	fmt.Println(colors, len(colors))

	// arrays are copied when assigned
	a := [3]int{1, 2, 3}
	b := a
	b[0] = 99
	fmt.Println(a, b)

	for index, value := range [3]string{"Go", "Python", "Rust"} {
		fmt.Printf("Index %d holds %s\n", index, value)
	}
}
