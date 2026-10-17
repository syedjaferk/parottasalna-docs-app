package textx

import (
	"errors"
	"reflect"
	"testing"
)

// A simple test: name starts with Test, takes *testing.T.
func TestWordCount(t *testing.T) {
	got, err := WordCount("Go go GO rocks")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := map[string]int{"go": 3, "rocks": 1}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("WordCount = %v, want %v", got, want)
	}
}

func TestWordCountEmpty(t *testing.T) {
	_, err := WordCount("   ")
	if !errors.Is(err, ErrEmpty) {
		t.Errorf("err = %v, want ErrEmpty", err)
	}
}

// Table-driven test: one loop, many cases, each with its own name.
func TestIsPalindrome(t *testing.T) {
	tests := []struct {
		name  string
		input string
		want  bool
	}{
		{"simple", "level", true},
		{"with spaces and case", "Never Odd Or Even", true},
		{"not one", "golang", false},
		{"empty", "", true},
		{"single letter", "a", true},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := IsPalindrome(tc.input); got != tc.want {
				t.Errorf("IsPalindrome(%q) = %v, want %v", tc.input, got, tc.want)
			}
		})
	}
}

// Benchmarks start with Benchmark and loop b.N times.
func BenchmarkIsPalindrome(b *testing.B) {
	for i := 0; i < b.N; i++ {
		IsPalindrome("Never Odd Or Even")
	}
}
