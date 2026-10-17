package main

import (
	"fmt"
	"time"
)

func task(name string, delay time.Duration) {
	for i := 1; i <= 3; i++ {
		fmt.Println(name, i)
		time.Sleep(delay)
	}
}

func main() {
	start := time.Now()
	// different delays make the interleaving predictable
	go task("slow", 200*time.Millisecond)
	go task("fast", 70*time.Millisecond)

	time.Sleep(700 * time.Millisecond) // a crude wait: see the next session for the proper one
	fmt.Println("took about", time.Since(start).Round(100*time.Millisecond))
}
