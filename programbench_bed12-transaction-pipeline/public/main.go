package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"
)

type Step struct {
	Op    string   `json:"op"`
	Name  string   `json:"name"`
	Text  string   `json:"text"`
	Tool  string   `json:"tool"`
	A     string   `json:"a"`
	B     string   `json:"b"`
	Flags []string `json:"flags"`
	Dest  string   `json:"dest"`
}
type Request struct {
	Files map[string]string `json:"files"`
	Steps []Step            `json:"steps"`
}
type Entry struct {
	Status string `json:"status"`
	Text   string `json:"text"`
}
type Result struct {
	Events []Entry           `json:"events"`
	Files  map[string]string `json:"files"`
}

func clone(x map[string]string) map[string]string {
	y := map[string]string{}
	for k, v := range x {
		y[k] = v
	}
	return y
}
func kernel(tool, a, b string, flags []string) (string, bool) { return "", false }
func solve(r Request) Result {
	fs := clone(r.Files)
	events := []Entry{}
	for _, s := range r.Steps {
		e := Entry{Status: "OK", Text: ""}
		switch s.Op {
		case "put":
			fs[s.Name] = s.Text
		case "get":
			var ok bool
			e.Text, ok = fs[s.Name]
			if !ok {
				e.Status = "MISSING"
			}
		case "list":
			keys := []string{}
			for k := range fs {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			e.Text = strings.Join(keys, "\n")
		case "run":
			e.Status = "TOOL_ERROR"
		default:
			e.Status = "NO_TX"
		}
		events = append(events, e)
	}
	return Result{events, fs}
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
