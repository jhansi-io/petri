package sandbox

import "time"

type Sandbox struct {
	ID			string
	Status		Status
	CreatedAt	time.Time
}
