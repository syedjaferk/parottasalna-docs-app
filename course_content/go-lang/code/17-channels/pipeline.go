package main

import "fmt"

func generate(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out) // closing tells the receiver "no more values"
		for _, n := range nums {
			out <- n
		}
	}()
	return out
}

func square(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in { // loop ends when in is closed
			out <- n * n
		}
	}()
	return out
}

func main() {
	for result := range square(generate(1, 2, 3, 4)) {
		fmt.Println(result)
	}
}
