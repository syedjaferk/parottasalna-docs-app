package main

import "fmt"

func counter() func() int {
	n := 0
	return func() int {
		n++
		return n
	}
}

func work() {
	defer fmt.Println("cleanup 1")
	defer fmt.Println("cleanup 2")
	fmt.Println("working...")
}

func main() {
	next := counter()
	fmt.Println(next(), next(), next())
	other := counter() // its own private n
	fmt.Println(other())

	work()

	for i := 1; i <= 3; i++ {
		defer fmt.Println("deferred", i)
	}
	fmt.Println("end of main")
}
