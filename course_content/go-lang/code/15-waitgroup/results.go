package main

import (
	"fmt"
	"strings"
	"sync"
)

func main() {
	words := []string{"go", "is", "fun", "and", "fast"}
	results := make([]string, len(words)) // one slot per goroutine: no clash

	var wg sync.WaitGroup
	for i, w := range words {
		wg.Add(1)
		go func() { // Go 1.22+: i and w are new on every iteration
			defer wg.Done()
			results[i] = strings.ToUpper(w)
		}()
	}
	wg.Wait()
	fmt.Println(results)
}
