package run

import "time"

type Run struct {
	ID 			string
	SandboxID	string
	Status		Status
	CreatedAt	time.Time
}
