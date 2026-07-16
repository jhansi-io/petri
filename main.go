package main

import (
	"log"
	"net/http"
	"github.com/jhansi-io/petri/internal/httpapi"
	"github.com/jhansi-io/petri/internal/sandbox"
)

func main() {
	registry := sandbox.NewRegistry()
	server := httpapi.NewServer(registry)
	log.Fatal(http.ListenAndServe(":8000", server.Routes()))
}
