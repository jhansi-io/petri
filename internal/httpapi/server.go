package httpapi

import (
	"net/http"
	"github.com/jhansi-io/petri/internal/sandbox"
)

type Server struct {
	sandboxes *sandbox.Registry
}

func NewServer(sandboxes *sandbox.Registry) *Server {
	return &Server{
		sandboxes: sandboxes,
	}
}

func (s *Server) Routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", s.health)
	mux.HandleFunc("POST /v1/sandboxes", s.createSandbox)
	return mux
}

func (s *Server) health(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ok"))
}
