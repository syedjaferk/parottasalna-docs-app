package main

import "fmt"

func main() {
	ch := make(chan string)

	go func() {
		ch <- "ping" // send: waits until someone receives
	}()

	msg := <-ch // receive: waits until someone sends
	fmt.Println(msg)

	// buffered: holds up to 2 values without a receiver
	buf := make(chan int, 2)
	buf <- 1
	buf <- 2
	fmt.Println(len(buf), cap(buf))
	fmt.Println(<-buf, <-buf)
}
