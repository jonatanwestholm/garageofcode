;(defun caar (x) (car (car x)))

;(write (caaar '(((a) b) c)))

(defun null. (x)
    (eq x '())
)

;(write (null. 'a))

(defun and. (x y)
    (cond (x (cond (y t))))
)

;(write (and. '() '()))

(defun not. (x)
    (cond (x '()) (t t))
)

;(write (not. '()))

(defun append. (x y)
    (cond 
        ((null. x) y)
        (t (cons (car x) 
                 (append. (cdr x) y)))
    )
)

;(write (append. '(a b c) '(e g)))

(defun pair. (x y)
    (cond
        ((and. (null. x) (null. y)) '())
        (t (cons 
            (list (car x) (car y))
            (pair. (cdr x) (cdr y))
            )
        )
    )
)

;(write (pair. '(a b c) '(i j k)))

(defun assoc. (x y)
    (cond
        ((null. y) '())
        ((eq x (caar y)) (cadar y))
        (t (assoc. x (cdr y)))
    )
)

;(write (assoc. 'b '((a c) (a e))))

