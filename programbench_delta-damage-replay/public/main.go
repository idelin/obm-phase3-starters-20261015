package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
)

type Config struct {
	Width   int  `json:"width"`
	Side    bool `json:"side"`
	Numbers bool `json:"numbers"`
	Tab     int  `json:"tab"`
}
type Step struct {
	Op     string   `json:"op"`
	At     int      `json:"at"`
	Delete int      `json:"delete"`
	Lines  []string `json:"lines"`
	Config Config   `json:"config"`
	Top    int      `json:"top"`
	Height int      `json:"height"`
}
type Request struct {
	Lines  []string `json:"lines"`
	Config Config   `json:"config"`
	Steps  []Step   `json:"steps"`
}
type Change struct {
	Row  int    `json:"row"`
	Text string `json:"text"`
}
type Entry struct {
	Status    string   `json:"status"`
	Total     int      `json:"total"`
	Screen    []string `json:"screen"`
	Changed   []Change `json:"changed"`
	ClearFrom int      `json:"clear_from"`
}
type Result struct {
	Events []Entry `json:"events"`
}

func render(lines []string, c Config) []string { return append([]string{}, lines...) }
func solve(r Request) Result {
	events := []Entry{}
	for _, s := range r.Steps {
		e := Entry{Status: "OK", Total: -1, Screen: []string{}, Changed: []Change{}, ClearFrom: -1}
		if s.Op == "frame" {
			e.Total = len(r.Lines)
			top := s.Top
			if top > len(r.Lines) {
				top = len(r.Lines)
			}
			end := top + s.Height
			if end > len(r.Lines) {
				end = len(r.Lines)
			}
			e.Screen = append([]string{}, r.Lines[top:end]...)
			for i, t := range e.Screen {
				e.Changed = append(e.Changed, Change{i, t})
			}
		}
		events = append(events, e)
	}
	return Result{events}
}
func main() {
	s := bufio.NewScanner(os.Stdin)
	s.Buffer(make([]byte, 4096), 32<<20)
	w := bufio.NewWriter(os.Stdout)
	defer w.Flush()
	for s.Scan() {
		var r Request
		if err := json.Unmarshal(s.Bytes(), &r); err != nil {
			panic(err)
		}
		b, _ := json.Marshal(solve(r))
		fmt.Fprintln(w, string(b))
	}
}
