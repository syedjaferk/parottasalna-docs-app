package main

import "fmt"

func main() {
	var s []int
	last := -1
	for i := 0; i < 20; i++ {
		s = append(s, i)
		if cap(s) != last {
			fmt.Printf("len=%2d cap=%2d\n", len(s), cap(s))
			last = cap(s)
		}
	}
}
