#!/usr/bin/env python3
"""Entfernt CSS-Regeln, deren Selektor eine Klasse enthält, die in keiner HTML-/JS-Datei des Ordners vorkommt (tote Regeln).
Aufruf: python3 tools/prune_css.py <ordner>     (idempotent; styles.css im Ordner wird überschrieben)"""
import re, sys, pathlib
root = pathlib.Path(sys.argv[1])
css = (root / "styles.css").read_text()
txt = "".join(p.read_text() for p in list(root.glob("*.html")) + [root / "main.js", root / "label.js"] if p.exists())

def strip_comments(s): return re.sub(r"/\*.*?\*/", "", s, flags=re.S)
classes = set(re.findall(r"\.([a-zA-Z_][\w-]*)", strip_comments(css)))
dead = {c for c in classes if not re.search(r"(?<![\w-])" + re.escape(c) + r"(?![\w-])", txt)}

def parse(s, i=0, end=None):
    """Liefert Liste von (prelude, body, kind) auf einer Ebene; Kommentare bleiben als ('', text, 'comment')."""
    out = []; n = len(s) if end is None else end
    while i < n:
        m = re.compile(r"\s*").match(s, i); j = m.end()
        if j >= n: out.append(("", s[i:j], "ws")); break
        if s.startswith("/*", j):
            k = s.index("*/", j) + 2; out.append(("", s[i:k], "comment")); i = k; continue
        b = s.index("{", j); prelude = s[j:b]
        depth = 1; k = b + 1
        while depth:
            if s[k] == "{": depth += 1
            elif s[k] == "}": depth -= 1
            k += 1
        out.append((prelude, s[b + 1:k - 1], "rule", s[i:j])); i = k
    return out

removed = []
def sel_dead(prelude):
    sels = [x for x in prelude.split(",")]
    return all(any(re.search(r"\." + re.escape(d) + r"(?![\w-])", x) for d in dead) for x in sels)

def render(items, level=0):
    res = []; 
    for it in items:
        if it[2] in ("comment", "ws"): res.append(it[1]); continue
        prelude, body, _, lead = it
        p = prelude.strip()
        if p.startswith("@media") or p.startswith("@supports"):
            inner = render(parse(body)); 
            if not re.sub(r"/\*.*?\*/|\s", "", inner, flags=re.S): removed.append(p); continue
            res.append(lead + prelude + "{" + inner + "}")
        elif p.startswith("@"):
            res.append(lead + prelude + "{" + body + "}")
        elif sel_dead(p):
            removed.append(p[:70]); 
        else:
            res.append(lead + prelude + "{" + body + "}")
    return "".join(res)

out = render(parse(css))
# Abschnittsüberschriften ohne Inhalt entfernen (Kommentar direkt vor nächstem Kommentar)
out = re.sub(r"(/\* ─── [^*]*?\*/\s*)(?=/\* ─── )", "", out)
out = re.sub(r"\n{3,}", "\n\n", out)
(root / "styles.css").write_text(out)
print(f"{len(removed)} tote Regeln entfernt; {len(css)//1024} KB -> {len(out)//1024} KB; tote Klassen: {sorted(dead)}")
