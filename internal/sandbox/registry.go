package sandbox

import "errors"

var ErrNotFound = errors.New("sandbox not found")

type Registry struct {
	sandboxes map[string]*Sandbox
}

func NewRegistry() *Registry {
	return &Registry{
		sandboxes: make(map[string]*Sandbox),
	}
}

func (r *Registry) Add(s *Sandbox) {
	r.sandboxes[s.ID] = s
}

func (r *Registry) Get(id string) (*Sandbox, error) {
	s, ok := r.sandboxes[id]
	if !ok {
		return nil, ErrNotFound
	}
	return s, nil
}
