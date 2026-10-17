package main

import (
	"fmt"
	"time"
)

func main() {
	fast := make(chan string)
	slow := make(chan string)
	go func() { time.Sleep(50 * time.Millisecond); fast <- "fast answer" }()
	go func() { time.Sleep(400 * time.Millisecond); slow <- "slow answer" }()

	// take whichever is ready first, but give up after 200ms
	for i := 0; i < 2; i++ {
		select {
		case m := <-fast:
			fmt.Println(m)
		case m := <-slow:
			fmt.Println(m)
		case <-time.After(200 * time.Millisecond):
			fmt.Println("timeout")
		}
	}

	// default: don't wait at all
	empty := make(chan int)
	select {
	case v := <-empty:
		fmt.Println(v)
	default:
		fmt.Println("nothing ready")
	}
}
