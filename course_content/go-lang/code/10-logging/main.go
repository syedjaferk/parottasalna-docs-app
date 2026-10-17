package main

import (
	"fmt"
	"log"
	"log/slog"
	"os"
)

func main() {
	// the plain standard logger: timestamp + message
	log.SetFlags(0) // drop the timestamp so the output is repeatable
	log.Println("server starting")
	log.SetPrefix("[app] ")
	log.Printf("listening on port %d", 8081)

	// slog: structured, with levels and key=value fields
	text := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
		ReplaceAttr: dropTime,
	}))
	text.Info("user logged in", "user", "Syed", "age", 28)
	text.Warn("validation failed", "field", "email")
	text.Debug("hidden: default level is Info")

	// the same call, JSON output for log tools
	js := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level:       slog.LevelDebug,
		ReplaceAttr: dropTime,
	}))
	js.Debug("now visible", "attempt", 2)
	js.With("app", "todo").Error("db down", "err", fmt.Errorf("timeout"))
}

func dropTime(groups []string, a slog.Attr) slog.Attr {
	if a.Key == slog.TimeKey {
		return slog.Attr{}
	}
	return a
}
