package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// bundle the lock with the data it protects
type SafeCounter struct {
	mu sync.Mutex
	n  map[string]int
}

func (c *SafeCounter) Inc(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.n[key]++
}

func main() {
	c := SafeCounter{n: map[string]int{}}
	var hits atomic.Int64 // for a single number, atomic is lighter than a mutex
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			c.Inc("page")
			hits.Add(1)
		}()
	}
	wg.Wait()
	fmt.Println(c.n["page"], hits.Load())
}
