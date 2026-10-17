package main

import "fmt"

type Counter struct{ n int }

func (c Counter) IncByValue()    { c.n++ } // works on a copy
func (c *Counter) IncByPointer() { c.n++ } // works on the original

func main() {
	c := Counter{}
	c.IncByValue()
	c.IncByValue()
	fmt.Println(c.n)
	c.IncByPointer()
	c.IncByPointer()
	fmt.Println(c.n)
}
