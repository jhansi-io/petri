package sandbox

import (
	"github.com/jhansi-io/petri/internal/id"
	"time"
)

type Sandbox struct {
	ID			string
	Status		Status
	CreatedAt	time.Time
}

func New() *Sandbox {
	return &Sandbox{
		ID: id.New("sb_"),
		Status: StatusCreating,
		CreatedAt: time.Now().UTC(),
	}
}
