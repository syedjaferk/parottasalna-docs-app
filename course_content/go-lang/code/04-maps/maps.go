package main

import (
	"fmt"
	"sort"
)

func main() {
	ages := make(map[string]int)
	ages["Vignesh"] = 26
	ages["Jafer"] = 28
	ages["Aron"] = 24

	fmt.Println(ages["Jafer"], len(ages))
	fmt.Println(ages["Nobody"]) // missing key: zero value

	value, exists := ages["Nobody"]
	fmt.Println(value, exists)
	if age, ok := ages["Aron"]; ok {
		fmt.Println("Aron is", age)
	}

	delete(ages, "Vignesh")

	// map order is random, so sort the keys when order matters
	keys := make([]string, 0, len(ages))
	for k := range ages {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Println(k, ages[k])
	}
}
