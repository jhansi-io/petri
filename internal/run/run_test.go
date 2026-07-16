package run

import (
	"strings"
	"testing"
)

func TestNew(t *testing.T) {
	r := New("sb_abc")

	if !strings.HasPrefix(r.ID, "run_") {
		t.Errorf("ID missing run_ prefix: %q", r.ID)
	}
	if r.SandboxID != "sb_abc" {
		t.Errorf("SandboxID = %q, want sb_abc", r.SandboxID)
	}
	if r.Status != StatusPreparing {
		t.Errorf("Status = %q, want PREPARING", r.Status)
	}
}
