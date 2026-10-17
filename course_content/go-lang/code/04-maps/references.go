package main

import "fmt"

func main() {
	m1 := map[string]int{"a": 1}
	m2 := m1 // same map, not a copy
	m2["a"] = 100
	fmt.Println(m1, m2)

	var nilMap map[string]int
	fmt.Println(nilMap["x"], len(nilMap)) // reading a nil map is fine
	defer func() { fmt.Println("recovered:", recover()) }()
	nilMap["x"] = 1 // writing panics
}
