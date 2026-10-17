package main

import "fmt"

func add(a, b int) int { return a + b }

// two results: a value and whether it worked
func divide(a, b float64) (float64, bool) {
	if b == 0 {
		return 0, false
	}
	return a / b, true
}

// named results
func minMax(nums []int) (min, max int) {
	min, max = nums[0], nums[0]
	for _, n := range nums {
		if n < min {
			min = n
		}
		if n > max {
			max = n
		}
	}
	return
}

// variadic: any number of ints
func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

func main() {
	fmt.Println(add(2, 3))

	q, ok := divide(10, 4)
	fmt.Println(q, ok)
	_, ok = divide(1, 0)
	fmt.Println(ok)

	lo, hi := minMax([]int{4, 9, 1, 7})
	fmt.Println(lo, hi)

	fmt.Println(sum(), sum(1, 2, 3))
	xs := []int{10, 20}
	fmt.Println(sum(xs...))
}
