import time
import pprint
from collections import defaultdict

def run(funcs, params):
    p_docs = [p_doc for p_doc, _ in params.items()]
    f_docs = [f_doc for f_doc, _ in funcs.items()]

    res = defaultdict(dict)
    for p_doc, p in params.items():
        for f_doc, func in funcs.items():
            t0 = time.time()
            r = func(*p)
            t1 = time.time()
            res[p_doc][f_doc] = (t1-t0, r)


    header_format = " " * 15 + "{:>15s}" * len(f_docs)
    print(header_format.format(*f_docs))
    row_format = "{:<15s}" + "{:>15.1f}" * len(f_docs)
    for p_doc, f2res in res.items():
        f2t = [1000*t for f_doc, (t, r) in f2res.items()]
        print(row_format.format(p_doc, *f2t))
    