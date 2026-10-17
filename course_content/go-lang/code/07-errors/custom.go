package main

import (
	"errors"
	"fmt"
)

type ValidationError struct {
	Field string
	Rule  string
}

func (e *ValidationError) Error() string {
	return e.Field + " " + e.Rule
}

func validate(age int) error {
	if age < 18 {
		return &ValidationError{Field: "age", Rule: "must be 18 or more"}
	}
	return nil
}

func main() {
	err := validate(15)
	fmt.Println(err)

	wrapped := fmt.Errorf("signup failed: %w", err)
	var ve *ValidationError
	if errors.As(wrapped, &ve) { // find a ValidationError anywhere in the chain
		fmt.Println("field:", ve.Field)
	}
	fmt.Println(validate(30) == nil)
}
