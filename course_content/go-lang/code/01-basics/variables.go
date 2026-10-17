package main

import "fmt"

func main() {
	var city string = "Coimbatore" // full form
	var year = 2026                // type inferred
	country := "India"             // short form, only inside functions
	const pi = 3.14159             // never changes

	var count int      // zero value: 0
	var ready bool     // zero value: false
	var label string   // zero value: "" (empty)

	fmt.Println(city, year, country, pi)
	fmt.Println(count, ready, label == "")
	fmt.Printf("%T %T %T %T\n", city, year, pi, ready)

	a, b := 7, 2
	fmt.Println(a/b, a%b, float64(a)/float64(b))
}
