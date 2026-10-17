package main

import "fmt"

func main() {
	s := []int{1, 2, 3}
	s = append(s, 4, 5)
	fmt.Println(s, len(s), cap(s))

	t := make([]int, 2, 10) // length 2, room for 10
	fmt.Println(t, len(t), cap(t))

	// slicing: [start:end), end not included
	fmt.Println(s[1:3], s[:2], s[3:])

	// a slice is a window onto the same array
	window := s[1:3]
	window[0] = 99
	fmt.Println(s, window)

	// copy makes an independent slice
	clone := make([]int, len(s))
	copy(clone, s)
	clone[0] = -1
	fmt.Println(s, clone)

	// removing index 1 by stitching two pieces
	s = append(s[:1], s[2:]...)
	fmt.Println(s)
}
