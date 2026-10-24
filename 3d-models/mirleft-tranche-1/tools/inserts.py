"""Walk the DWG JSON and list every INSERT with its world transform. python -I inserts.py in.json out.pkl"""
import json, math, pickle, sys
db = json.load(open(sys.argv[1]))
BLK = {b['name']: b for b in db['tables']['BLOCK_RECORD']['entries']}
out = []
def mat(ins, base):
    sx, sy = ins.get('xScale', 1) or 1, ins.get('yScale', 1) or 1
    r = ins.get('rotation', 0) or 0
    ex = ins.get('extrusionDirection', {}).get('z', 1)
    p = ins['insertionPoint']; bx, by = base[0], base[1]
    c, s = math.cos(r), math.sin(r)
    fx = -1 if ex < 0 else 1
    # affine: world = A @ (local - base) + p ; with mirror for extrusion -z
    A = [[c * sx * fx, -s * sy], [s * sx * fx, c * sy]]
    return A, (p['x'], p['y']), (bx, by)
def compose(F, A, t, b):
    (FA, Ft) = F
    # local -> parent: q = A (x - b) + t ; parent -> world: F
    NA = [[FA[0][0] * A[0][0] + FA[0][1] * A[1][0], FA[0][0] * A[0][1] + FA[0][1] * A[1][1]],
          [FA[1][0] * A[0][0] + FA[1][1] * A[1][0], FA[1][0] * A[0][1] + FA[1][1] * A[1][1]]]
    tt = (t[0] - A[0][0] * b[0] - A[0][1] * b[1], t[1] - A[1][0] * b[0] - A[1][1] * b[1])
    Nt = (FA[0][0] * tt[0] + FA[0][1] * tt[1] + Ft[0], FA[1][0] * tt[0] + FA[1][1] * tt[1] + Ft[1])
    return (NA, Nt)
def walk(ents, F, path):
    for e in ents:
        if e.get('type') != 'INSERT': continue
        b = BLK.get(e['name'])
        bp = (b or {}).get('basePoint') or {'x': 0, 'y': 0}
        A, t, base = mat(e, (bp.get('x', 0), bp.get('y', 0)))
        G = compose(F, A, t, base)
        (GA, Gt) = G
        rot = math.degrees(math.atan2(GA[1][0], GA[0][0]))
        det = GA[0][0] * GA[1][1] - GA[0][1] * GA[1][0]
        bw = (GA[0][0] * base[0] + GA[0][1] * base[1] + Gt[0], GA[1][0] * base[0] + GA[1][1] * base[1] + Gt[1])
        out.append(dict(name=e['name'], layer=e.get('layer'), path=path, A=GA, t=Gt, base=base, p=bw, rot=rot, mirror=det < 0,
                        scale=math.sqrt(abs(det))))
        if b and b.get('entities'):
            walk(b['entities'], G, path + [e['name']])
ms = BLK['*Model_Space']
walk(ms['entities'], ([[1, 0], [0, 1]], (0, 0)), [])
pickle.dump(out, open(sys.argv[2], 'wb'))
print(len(out))
