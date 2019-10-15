import time
import pprint
from collections import defaultdict

def run(funcs, params, validate=True, **kwargs):
    p_docs = [p_doc for p_doc, _ in params.items()]
    f_docs = [f_doc for f_doc, _ in funcs.items()]
    width = max(max(map(len, p_docs)), max(map(len, f_docs)) + 2)

    if validate:
        header_format = "{0:<{1}}".format("time / ms", width) + "".join(["{" + ":>{}s".format(width) + "}"] * len(f_docs)) * 2
        header_format = header_format + "{0:>{1}}".format("all equal", width)
        print(header_format.format(*f_docs, *f_docs))
    else:
        header_format = "{0:<{1}}".format("time / ms", width) + "".join(["{" + ":>{}s".format(width) + "}"] * len(f_docs))
        print(header_format.format(*f_docs))

    #row_format = "{:<15s}" + "{:>15}" * len(f_docs) + "{:>15}" * len(f_docs) + "{:>15}"

    res = {}
    for p_doc, p in params.items():
        res[p_doc] = {f_doc: ("", "") for f_doc in funcs}
        print_row(p_doc, res[p_doc], width, validate, **kwargs)
        for f_doc, func in funcs.items():
            t0 = time.time()
            r = func(*p)
            t1 = time.time()
            res[p_doc][f_doc] = (t1-t0, r)
            print_row(p_doc, res[p_doc], width, validate, **kwargs)
        print()


def print_row(p_doc, f2res, width, validate, decimals=1):
    # TODO: calculate appropriate accuracy in milliseconds
    row_format = ""
    for _, (t, r) in f2res.items():
        if type(t) == type(""):
            row_format = row_format + "{" + ":>{0}s".format(width) + "}"
        else:
            row_format = row_format + "{" + ":>{0}.{1}f".format(width, decimals) + "}"
    if validate:
        row_format = row_format * 2
    row_format = "{" + ":<{}s".format(width) + "}" + row_format
    if validate:
        row_format = row_format + "{" + ":>{}s".format(width) + "}"

    f2t, f2r = zip(*[(1000*t, r) for f_doc, (t, r) in f2res.items()])
    if validate:
        all_equal = "ok" if all([f2r[0] == r for r in f2r]) else "not"
        print(row_format.format(p_doc, *f2t, *f2r, all_equal), end="\r")
    else:
        print(row_format.format(p_doc, *f2t), end="\r")

    