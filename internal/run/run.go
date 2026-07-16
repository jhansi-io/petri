package run

import (
	"github.com/jhansi-io/petri/internal/id"
	"time"
)

type Run struct {
	ID 			string
	SandboxID	string
	Status		Status
	CreatedAt	time.Time
}

func New(sandboxID string) *Run {
	return &Run{
		ID: id.New("run_"),
		SandboxID: sandboxID,
		Status: StatusPreparing,
		CreatedAt: time.Now().UTC(),
	}
}
