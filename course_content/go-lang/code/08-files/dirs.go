package main

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
)

func main() {
	os.MkdirAll("project/docs/img", 0755)
	os.WriteFile("project/main.go", []byte("package main"), 0644)
	os.WriteFile("project/docs/readme.md", []byte("# hi"), 0644)
	os.WriteFile("project/docs/img/logo.png", []byte("x"), 0644)

	entries, _ := os.ReadDir("project")
	for _, e := range entries {
		fmt.Println(e.Name(), e.IsDir())
	}

	// walk the whole tree
	filepath.WalkDir("project", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if !d.IsDir() {
			info, _ := d.Info()
			fmt.Println(path, info.Size(), "bytes", filepath.Ext(path))
		}
		return nil
	})
}
