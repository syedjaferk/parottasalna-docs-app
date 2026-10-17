package main

import (
	"errors"
	"fmt"
	"strconv"
)

var ErrNegative = errors.New("negative number")

func parsePositive(s string) (int, error) {
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("parsePositive %q: %w", s, err) // wrap with context
	}
	if n < 0 {
		return 0, fmt.Errorf("parsePositive %d: %w", n, ErrNegative)
	}
	return n, nil
}

func main() {
	for _, in := range []string{"42", "abc", "-5"} {
		n, err := parsePositive(in)
		if err != nil {
			fmt.Println("error:", err)
			fmt.Println("  is negative?", errors.Is(err, ErrNegative))
			continue
		}
		fmt.Println("ok:", n)
	}
}
