package main

import "fmt"

type Address struct {
	Street string
	City   string
}

type Person struct {
	Name    string
	Age     int
	Active  bool
	Address Address // a struct inside a struct
}

// a method: a function attached to Person
func (p Person) IsEligibleToVote() bool {
	return p.Age >= 18
}

func main() {
	p := Person{
		Name:    "Jafer",
		Age:     25,
		Address: Address{Street: "2nd Street", City: "Coimbatore"},
	}
	fmt.Println(p)
	fmt.Printf("%+v\n", p)

	p.Age = 28
	fmt.Println(p.Name, p.Age, p.Address.City, p.IsEligibleToVote())

	var empty Person
	fmt.Printf("%+v\n", empty)
}
