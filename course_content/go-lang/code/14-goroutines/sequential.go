package main

import (
	"fmt"
	"time"
)

func task(name string) {
	for i := 1; i <= 3; i++ {
		fmt.Println(name, i)
		time.Sleep(100 * time.Millisecond)
	}
}

func main() {
	start := time.Now()
	task("Task 1")
	task("Task 2") // starts only after Task 1 is completely done
	fmt.Println("took about", time.Since(start).Round(100*time.Millisecond))
}
