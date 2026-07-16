package sandbox

import (
	"crypto/rand"
	"encoding/hex"
	"time"
)

type Sandbox struct {
	ID			string
	Status		Status
	CreatedAt	time.Time
}

func New() *Sandbox {
	return &Sandbox{
		ID: "sb_" + randomHex(16),
		Status: StatusCreating,
		CreatedAt: time.Now().UTC(),
	}
}

func randomHex(n int) string {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return hex.EncodeToString(b)
}
