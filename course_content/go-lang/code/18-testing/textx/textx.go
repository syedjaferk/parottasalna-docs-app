// Package textx holds a few small text helpers to practise testing.
package textx

import (
	"errors"
	"strings"
)

var ErrEmpty = errors.New("empty input")

// WordCount returns how many times each word appears, ignoring case.
func WordCount(s string) (map[string]int, error) {
	fields := strings.Fields(strings.ToLower(s))
	if len(fields) == 0 {
		return nil, ErrEmpty
	}
	counts := make(map[string]int)
	for _, w := range fields {
		counts[w]++
	}
	return counts, nil
}

// IsPalindrome reports whether s reads the same forwards and backwards,
// ignoring case and spaces.
func IsPalindrome(s string) bool {
	var letters []rune
	for _, r := range strings.ToLower(s) {
		if r != ' ' {
			letters = append(letters, r)
		}
	}
	for i, j := 0, len(letters)-1; i < j; i, j = i+1, j-1 {
		if letters[i] != letters[j] {
			return false
		}
	}
	return true
}
