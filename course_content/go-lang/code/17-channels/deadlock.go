package main

import "fmt"

func main() {
	ch := make(chan int)
	ch <- 1 // nobody is receiving: main waits forever
	fmt.Println(<-ch)
}
