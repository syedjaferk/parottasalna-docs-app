package main

import (
	"fmt"
	"sort"
	"sync"
)

func worker(id int, jobs <-chan int, results chan<- string, wg *sync.WaitGroup) {
	defer wg.Done()
	for j := range jobs {
		results <- fmt.Sprintf("job %d -> %d", j, j*j)
	}
}

func main() {
	jobs := make(chan int, 10)
	results := make(chan string, 10)

	var wg sync.WaitGroup
	for id := 1; id <= 3; id++ { // three workers share one queue
		wg.Add(1)
		go worker(id, jobs, results, &wg)
	}
	for j := 1; j <= 6; j++ {
		jobs <- j
	}
	close(jobs)

	wg.Wait()
	close(results)

	var lines []string
	for r := range results {
		lines = append(lines, r)
	}
	sort.Strings(lines) // workers finish in any order, so sort for stable output
	for _, l := range lines {
		fmt.Println(l)
	}
}
