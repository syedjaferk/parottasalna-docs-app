package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {
	var (
		dir     string
		ext     string
		verbose bool
		limit   int
	)
	flag.StringVar(&dir, "dir", "", "directory to search")
	flag.StringVar(&ext, "ext", "", "only files with this extension")
	flag.BoolVar(&verbose, "verbose", false, "print extra detail")
	flag.IntVar(&limit, "limit", 0, "max results (0 = all)")
	flag.Usage = func() {
		fmt.Println("Usage: finder -dir=<dir> [-ext=.go] [-verbose] [-limit=N]")
		flag.PrintDefaults()
	}
	flag.Parse()

	if dir == "" {
		fmt.Println("Error: -dir is required")
		flag.Usage()
		os.Exit(1)
	}
	fmt.Println("dir:", dir, "ext:", ext, "verbose:", verbose, "limit:", limit)
	fmt.Println("leftover args:", flag.Args())
}
