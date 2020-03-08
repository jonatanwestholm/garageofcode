package main

import (
	"fmt"
	"github.com/google/go-cmp/cmp"
	"garageofcode/hello/morestrings"
)

func main(){
	fmt.Println("Hello, Go!")
	fmt.Println(morestrings.ReverseRunes("Hello, Go!"))
	fmt.Println(cmp.Diff("Hello, Go!", "Hello world!"))
}