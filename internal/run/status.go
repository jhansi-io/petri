package run

type Status string

const (
	StatusPreparing	Status = "PREPARING"
	StatusRunning	Status = "RUNNING"
	StatusSucceeded	Status = "SUCCEEDED"
	StatusFailed	Status = "FAILED"
	StatusTimedOut	Status = "TIMED_OUT"
	StatusError		Status = "ERROR"
)
