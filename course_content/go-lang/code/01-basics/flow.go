package main

import "fmt"

func main() {
	age := 16
	if age >= 18 {
		fmt.Println("Eligible to vote")
	} else {
		fmt.Println("Not eligible yet")
	}

	// the classic three-part loop
	for i := 1; i <= 3; i++ {
		fmt.Println("lap", i)
	}

	// Go has no while: a for with only a condition
	n := 3
	for n > 0 {
		fmt.Println("countdown", n)
		n--
	}

	// switch: no break needed, first match wins
	day := 6
	switch day {
	case 6, 7:
		fmt.Println("weekend")
	default:
		fmt.Println("weekday")
	}

	// if with a short statement before the condition
	if square := age * age; square > 200 {
		fmt.Println("big square", square)
	}
}
