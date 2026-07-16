package sandbox

import (
	"strings"
	"testing"
)

func TestNew(t *testing.T) {
	s := New()
	if !strings.HasPrefix(s.ID, "sb_") {
		t.Errorf("ID missing sb_ prefix: %q", s.ID)
	}
	if s.Status != StatusCreating {
		t.Errorf("Status = %q, want CREATING", s.Status)
	}
}
