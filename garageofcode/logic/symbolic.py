class Expression:
    def __init__(self, op, lhs, rhs=None):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        if self.rhs is None:
            return str(self.op) + "(" + str(self.lhs) + ")"
        else:
            return str(self.lhs) + self.op + str(self.rhs)


def differentiate(expr, x):
    print(expr)
    try:
        expr.op
    except AttributeError:
        if expr == x:
            return 1
        else:
            return 0

    if expr.op in ["+", "-"]:
        return Expression(expr.op,
                          differentiate(expr.lhs, x),
                          differentiate(expr.rhs, x)
                          )
    elif expr.op == "*":
        return Expression("+",
                          Expression("*",
                                     differentiate(expr.lhs, x),
                                     expr.rhs
                                     ),
                          Expression("*",
                                     expr.lhs,
                                     differentiate(expr.rhs, x)
                                    )
                         )
    elif expr.op == "/":
        return Expression("-",
                          Expression("/",
                                     differentiate(expr.lhs, x),
                                     expr.rhs
                                     ),
                          Expression("/",
                                     Expression("*",
                                                expr.lhs,
                                                differentiate(expr.rhs, x)
                                                ),
                                     Expression("*",
                                                expr.rhs,
                                                expr.rhs
                                                )
                                    )
                          )

def main():
    expr = Expression("/", 2, "x")
    print(differentiate(expr, "x"))


if __name__ == '__main__':
    main()


