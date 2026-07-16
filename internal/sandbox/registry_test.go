package sandbox

import (
	"errors"
	"testing"
)

func TestRegistryAddGet(t *testing.T) {
	r := NewRegistry()
	s := New()

	r.Add(s)

	got, err := r.Get(s.ID)
	if err != nil {
		t.Fatalf("Get after Add: unexpected error %v", err)
	}
	if got.ID != s.ID {
		t.Errorf("got ID %q, want %q", got.ID, s.ID)
	}
}

func TestRegistryGetMissing(t *testing.T) {
	r := NewRegistry()

	_, err := r.Get("sb_nope")
	if !errors.Is(err, ErrNotFound) {
		t.Errorf("got error %v, want ErrNotFound", err)
	}
}
