package main

import "fmt"

func safeDivide(a, b int) (result int, err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("recovered: %v", r)
		}
	}()
	return a / b, nil // integer divide by zero panics
}

func main() {
	fmt.Println(safeDivide(10, 2))
	fmt.Println(safeDivide(1, 0))
}
