
def get_subexpr(s):
    d = 1
    for i, ch in enumerate(s):
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if not d:
            break
    else:
        raise # Unmatched left parenthesis
    return s[:i]


def get_token(s):
    s = s.strip()
    


def tokenize(s):
    while s:
        tok, s = get_token(s)
        if tok == "(":
            sub_s, s = get_subexpr(s)
            yield parse(s)
        else:
            yield tok


def parse(s):
    tokens = list(tokenize(s))
    # magic happens, returns an expression



class Expression:
    def __init__(self, op, lhs, rhs=None):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        if self.rhs is None:
            return str(self.op) + "(" + str(self.lhs) + ")"
        else:
            return "(" + str(self.lhs) + self.op + str(self.rhs) + ")"

    def simplify(self):
        try:
            self.lhs = self.lhs.simplify()
        except AttributeError:
            pass

        try:
            self.rhs = self.rhs.simplify()
        except AttributeError:
            pass

        if self.op == "+":
            try:
                return self.lhs + self.rhs / 1
            except TypeError:
                pass

            if self.lhs == 0:
                return self.rhs
            if self.rhs == 0:
                return self.lhs
            return self

        if self.op == "-":
            try:
                return self.lhs - self.rhs
            except TypeError:
                pass

            if self.lhs == 0:
                return Expression("*", -1, self.rhs).simplify()
            if self.rhs == 0:
                return self.lhs
            return self

        if self.op == "*":
            try:
                return self.lhs * self.rhs / 1
            except TypeError:
                pass

            if self.rhs == 0:
                return 0
            if self.lhs == 0:
                return 0
            if self.lhs == 1:
                return self.rhs
            if self.rhs == 1:
                return self.lhs
            return self

        if self.op == "/":
            try:
                return self.lhs / self.rhs
            except TypeError:
                pass

            if self.lhs == 0:
                return 0
            if self.lhs == 1:
                return self
            if self.rhs == 1:
                return self.lhs
            return self


def differentiate(expr, x):
    #print(expr)
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
    expr = Expression("*", 2, "x")
    print(expr.simplify())
    #print(differentiate(expr, "x").simplify())


if __name__ == '__main__':
    main()


