package main

import(
	"fmt"
	"time"
)

/*
*/
func num_combs(vals []int, target int, num_vals int) int{
	if target == 0{
		return 1
	}

	if target < 0{
		return 0
	}

	if num_vals == 0{
		return 0
	}

	return num_combs(vals, target - vals[0], num_vals) + 
			num_combs(vals[1:], target, num_vals - 1)
}


func main(){
	num_vals := 8
	target := 500
	vals := []int{200, 100, 50, 20, 10, 5, 2, 1}
	//fmt.Println(vals[:len(vals) - 3])
	t0 := time.Now()
	fmt.Println(num_combs(vals, target, num_vals))
	fmt.Println(time.Since(t0))
}