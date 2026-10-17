package main

import (
	"fmt"
	"sync"
	"time"
)

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done() // tell the group "I'm finished", even on early return
	time.Sleep(time.Duration(id) * 50 * time.Millisecond)
	fmt.Println("worker", id, "finished")
}

func main() {
	var wg sync.WaitGroup
	for i := 1; i <= 3; i++ {
		wg.Add(1) // add before starting the goroutine
		go worker(i, &wg)
	}
	wg.Wait() // blocks until the counter is back to zero
	fmt.Println("All workers completed")
}
