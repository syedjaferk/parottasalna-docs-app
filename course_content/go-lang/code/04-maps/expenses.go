package main

import (
	"fmt"
	"sort"
)

type Expense struct {
	Description string
	Amount      float64
	Category    string
}

var expenses = map[int]Expense{}

func add(id int, e Expense) { expenses[id] = e }

func update(id int, amount float64) {
	e, ok := expenses[id]
	if !ok {
		fmt.Println("Expense not found:", id)
		return
	}
	e.Amount = amount // e is a copy, so store it back
	expenses[id] = e
}

func main() {
	add(1, Expense{"Tea", 20, "Food"})
	add(2, Expense{"Bus", 35.5, "Travel"})
	update(1, 25)
	update(9, 1)

	ids := make([]int, 0)
	for id := range expenses {
		ids = append(ids, id)
	}
	sort.Ints(ids)

	total := 0.0
	byCategory := map[string]float64{}
	for _, id := range ids {
		e := expenses[id]
		fmt.Printf("%d %-4s %6.2f %s\n", id, e.Description, e.Amount, e.Category)
		total += e.Amount
		byCategory[e.Category] += e.Amount
	}
	fmt.Println("total:", total, byCategory)
}
