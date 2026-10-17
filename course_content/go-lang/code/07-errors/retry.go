package main

import (
	"errors"
	"fmt"
	"time"
)

var calls int

func flaky() error {
	calls++
	if calls < 3 {
		return fmt.Errorf("attempt %d: server busy", calls)
	}
	return nil
}

func retry(attempts int, delay time.Duration, fn func() error) error {
	var errs []error
	for i := 1; i <= attempts; i++ {
		err := fn()
		if err == nil {
			fmt.Println("succeeded on attempt", i)
			return nil
		}
		fmt.Println("failed:", err)
		errs = append(errs, err)
		time.Sleep(delay)
		delay *= 2 // wait longer each time
	}
	return fmt.Errorf("gave up after %d attempts: %w", attempts, errors.Join(errs...))
}

func main() {
	fmt.Println(retry(5, 10*time.Millisecond, flaky))

	err := retry(2, time.Millisecond, func() error { return errors.New("server down") })
	fmt.Println(err)
}
