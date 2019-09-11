#|
(write
    (cond 
        ((eq 'a 'b)
            (+ 1 2)) 
        ((eq 'a 'c)
            'baloney)
        (t 'default)
    )
)
(write
    ((lambda (z) (z '(b c)))
        '(lambda (x) (cons 'a x))
    )
)


(defun f (z) (z 'b))

(write
    (f '(lambda (x) (cons 'a x)))
)

;((lambda (f) (funcall f '(b c))) '(lambda (x) (cons 'a x)))
(write
    ((lambda (f) (funcall f '(b c ))) (lambda (x) (cons 'a x)))
)
(defun l_subst (x y z) 
    (cond 
        ((atom z) 
            (cond 
                ((eq z y) x)
                (t z)
            )
        )
        (t 
            (cons (l_subst x y (car z))
                  (l_subst x y (cdr z))
            )
        )
    )
)

(write 
    (l_subst 'b 'z '('a 'z 'z 'a))
)
|#

;((lambda (f) ((lambda (x) (cons 'a x)) 'b)) 'q)

;(defun f (x) (cons 'a x))

;(write (f 'b))

;(write (f 'b))

;((lambda (x) (cons 'a x)) '(b c))