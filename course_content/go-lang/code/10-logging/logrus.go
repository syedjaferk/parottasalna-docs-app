package main

import (
	log "github.com/sirupsen/logrus"
)

func main() {
	log.SetFormatter(&log.JSONFormatter{DisableTimestamp: true})
	log.SetLevel(log.InfoLevel)

	log.WithField("app", "todo").Info("Application started")
	log.WithFields(log.Fields{"user": "Syed Jafer", "age": 28}).Warn("User validation failed")
	log.Debug("not shown at Info level")
}
