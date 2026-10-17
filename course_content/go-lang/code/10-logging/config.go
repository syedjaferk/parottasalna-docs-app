package main

import (
	"fmt"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	App struct {
		Name string `yaml:"name"`
	} `yaml:"app"`
	Validation struct {
		MinAge int `yaml:"min_age"`
	} `yaml:"validation"`
	Logging struct {
		Level string `yaml:"level"`
	} `yaml:"logging"`
}

func LoadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("parse %s: %w", path, err)
	}
	return &cfg, nil
}

func main() {
	cfg, err := LoadConfig("10-logging/config.yaml")
	if err != nil {
		fmt.Println("error:", err)
		return
	}
	fmt.Printf("%+v\n", *cfg)
	fmt.Println(cfg.App.Name, cfg.Validation.MinAge)

	_, err = LoadConfig("nope.yaml")
	fmt.Println(err)
}
