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


(defun evcon. (c a)
    (cond ((eval. (caar c) a)
           (eval. (cadar c) a))
          ('t (evcon. (cdr c) a))))

(defun evlis. (m a)
    (cond ((null. m) '())
           ('t (cons (eval. (car m) a)
                     (evlis. (cdr m) a)))))

(defun eval. (e a)
    (cond
        ((atom e) (assoc. e a))
        ((atom (car e))
            (cond
            ((eq (car e) 'quote) (cadr e))
            ((eq (car e) 'atom) (atom (eval. (cadr e) a)))
            ((eq (car e) 'eq) (eq (eval. (cadr e) a)
                                  (eval. (caddr e) a)))
            ((eq (car e) 'car) (car (eval. (cadr e) a)))
            ((eq (car e) 'cdr) (cdr (eval. (cadr e) a)))
            ((eq (car e) 'cons) (cons (eval. (cadr e) a)
                                      (eval. (caddr e) a)))
            ((eq (car e) 'cond) (evcon. (cdr e) a))
            ('t (eval. (cons (assoc. (car e) a)
                             (cdr e))
            a))))
        ((eq (caar e) 'label.)
            (eval. (cons (caddar e) (cdr e))
                   (cons (list (cadar e) (car e)) a)))
        ((eq (caar e) 'lambda.)
            (eval. (caddar e)
                   (append. (pair. (cadar e) (evlis. (cdr e) a))
                            a)))))

;(defun defun. (f args exp))

; ok, challenge: define "defun." without using defun, only eval.
; I want to be able to write:
;(defun. f (x) (+ x 1))
;(write (f 1)) ;should return 2

(eval. 
    ((label defun. (lambda. (fname args expr) ()))
     ((defun. f (x) (+ x 1))
      (write (f 1)))
    ) 
    '())



#|
(write 
    (eval. 'a 
           '((a x) (b y))))
|#

