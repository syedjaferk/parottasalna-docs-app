package main

import "fmt"

func main() {
	x := 10
	p := &x // p holds the address of x
	fmt.Println(x, *p)
	fmt.Println(p == &x)

	*p = 20 // change x through p
	fmt.Println(x)

	var nothing *int
	fmt.Println(nothing == nil)
}
