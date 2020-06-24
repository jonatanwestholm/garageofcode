import numpy as np

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
    return s[:i], s[i:]


def get_token(s):
    """
    Unary minus sign is a big bug
    """
    s = s.strip()
    for pat in ["+", "-", "*", "/", "(", ")", "cos(", "sin("]:
        if s.startswith(pat):
            return s[:len(pat)], s[len(pat):]

    for i, ch in enumerate(s):
        #print("ch:", ch)
        if not ch.isalnum():
            break
    else:
        return s, ""
    return s[:i], s[i:]


def tokenize(s):
    s = s.strip()
    while s:
        tok, s = get_token(s)
        if tok == "(":
            sub_s, s = get_subexpr(s)
            #print("sub_s:", sub_s)
            #print("s:", s)
            yield parse(sub_s)
        elif tok == "cos(":
            sub_s, s = get_subexpr(s)
            yield Expression("cos", parse(sub_s))
        elif tok == "sin(":
            sub_s, s = get_subexpr(s)
            yield Expression("sin", parse(sub_s))
        elif tok == ")":
            pass
        else:
            yield tok


def parse(s):
    tokens = list(tokenize(s))
    
    newtokens = []
    for tok in tokens:
        try:
            tok = int(tok)
        except ValueError:
            pass
        except TypeError:
            pass
        newtokens.append(tok)
    tokens = newtokens

    while len(tokens) > 1:
        if "/" in tokens:
            i = tokens.index("/")
            expr = Expression("/", tokens[i-1], tokens[i+1])
            tokens = tokens[:i-1] + [expr] + tokens[i+2:]
            continue

        if "*" in tokens:
            i = tokens.index("*")
            expr = Expression("*", tokens[i-1], tokens[i+1])
            tokens = tokens[:i-1] + [expr] + tokens[i+2:]
            continue

        if "-" in tokens:
            i = tokens.index("-")
            expr = Expression("-", tokens[i-1], tokens[i+1])
            tokens = tokens[:i-1] + [expr] + tokens[i+2:]
            continue

        if "+" in tokens:
            i = tokens.index("+")
            expr = Expression("+", tokens[i-1], tokens[i+1])
            tokens = tokens[:i-1] + [expr] + tokens[i+2:]
            continue

    return tokens[0]


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

        if self.op == "cos":
            try:
                return np.cos(self.lhs)
            except TypeError:
                return self

        if self.op == "sin":
            try:
                return np.sin(self.lhs)
            except TypeError:
                return self

    def collect_literals(self):
        try:
            self.lhs.collect_literals()
        except AttributeError:
            lhs_literals = {1: self.lhs}

        try:
            self.rhs.collect_literals()
        except AttributeError:
            rhs_literals = {1: self.rhs}

        self.literals = {}
        if self.op == "+":
            pass


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
    elif expr.op == "sin":
        return Expression("*", 
                          differentiate(expr.lhs, x), 
                          Expression("cos", expr.lhs)
                        )
    elif expr.op == "cos":
        return Expression("*", 
                          -1, 
                          Expression("*", 
                                     differentiate(expr.lhs, x),
                                     Expression("sin", expr.lhs)
                                    )
                        )

def main():
    #expr = Expression("*", 2, "x")
    #print(expr.simplify())
    #print(differentiate(expr, "x").simplify())

    print(differentiate(parse("cos(x)*cos(x) + sin(x)*sin(x)"), "x").simplify())



if __name__ == '__main__':
    main()


