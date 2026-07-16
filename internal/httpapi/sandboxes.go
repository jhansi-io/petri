package httpapi

import (
	"encoding/json"
	"net/http"
	"github.com/jhansi-io/petri/internal/sandbox"
)

type sandboxResponse struct {
	ID 		string `json:"id"`
	Status	string `json:"status"`
}

func (s *Server) createSandbox(w http.ResponseWriter, r *http.Request) {
	sb := sandbox.New()
	s.sandboxes.Add(sb)

	resp := sandboxResponse{
		ID: sb.ID,
		Status: string(sb.Status),
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(resp)
}
