#|
|#
(format t 
    (string 
        (cond 
            ((eq 'a 'b) 'first) 
            ((eq 'a 'c) 'second) 
            (t 'default)
        )
    )
)