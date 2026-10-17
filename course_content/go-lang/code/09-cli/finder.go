package main

import (
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
)

func main() {
	dir := flag.String("dir", "", "directory to search")
	ext := flag.String("ext", "", "extension filter, like .go")
	limit := flag.Int("limit", 0, "max results")
	flag.Parse()

	info, err := os.Stat(*dir)
	if err != nil || !info.IsDir() {
		fmt.Println("Error: not a directory:", *dir)
		os.Exit(1)
	}

	found := 0
	filepath.WalkDir(*dir, func(path string, d fs.DirEntry, err error) error {
		if err != nil || d.IsDir() {
			return err
		}
		if *ext != "" && filepath.Ext(path) != *ext {
			return nil
		}
		if *limit > 0 && found >= *limit {
			return filepath.SkipAll
		}
		fmt.Println(path)
		found++
		return nil
	})
	fmt.Println("found", found)
}
