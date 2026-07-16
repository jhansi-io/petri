package sandbox

type Status string

const (
	StatusCreating	Status = "CREATING"
	StatusReady		Status = "READY"
	StatusExpired	Status = "EXPIRED"
	StatusDeleted	Status = "DELETED"
	StatusError		Status = "ERROR"
)
