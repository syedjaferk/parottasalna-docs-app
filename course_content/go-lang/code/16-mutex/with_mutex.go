package main

import (
	"fmt"
	"sync"
)

var (
	counter int
	mutex   sync.Mutex
)

func increment(wg *sync.WaitGroup) {
	defer wg.Done()
	for i := 0; i < 1000000; i++ {
		mutex.Lock()
		counter++
		mutex.Unlock()
	}
}

func main() {
	var wg sync.WaitGroup
	wg.Add(2)
	go increment(&wg)
	go increment(&wg)
	wg.Wait()
	fmt.Println("expected 2000000, got", counter)
}
