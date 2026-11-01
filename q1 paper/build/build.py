#!/usr/bin/env python3
"""Assemble q1 paper/manuscript.md from the keyed section files.

- Concatenates build/NN_*.md in name order.
- Replaces pandoc-style [@a; @b] citations with IEEE numbers [1], [2]
  in order of first appearance.
- Writes the References section from the source .bib (fields as given).
- Writes q1 paper/references.bib with only the cited entries, copied
  verbatim from research paper/references.bib.

Usage: python3 build.py   (run from any directory)
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_BIB = os.path.join(os.path.dirname(ROOT), "research paper", "references.bib")


def parse_bib(text):
    entries = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),", text):
        typ, key = m.group(1).lower(), m.group(2).strip()
        i, depth = m.end(), 1
        while depth and i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        raw = text[m.start():i]
        body = text[m.end():i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            j = fm.end()
            if body[j] == "{":
                d, k = 1, j + 1
                while d:
                    d += {"{": 1, "}": -1}.get(body[k], 0)
                    k += 1
                val = body[j + 1:k - 1]
            else:
                k = j
                while k < len(body) and body[k] not in ",\n":
                    k += 1
                val = body[j:k]
            fields[fm.group(1).lower()] = val
        entries[key] = (typ, fields, raw)
    return entries


def clean(s):
    s = re.sub(r"\\url\{([^}]*)\}", r"\1", s)
    s = s.replace("\\&", "&").replace("\\_", "_").replace("---", "-").replace("--", "-")
    s = s.replace("``", '"').replace("''", '"')
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def authors(a):
    names = [clean(x) for x in re.split(r"\s+and\s+", a)]
    out = []
    for n in names:
        if "," in n:
            last, first = [p.strip() for p in n.split(",", 1)]
            initials = " ".join(p[0] + "." for p in re.split(r"[\s-]+", first) if p)
            out.append(f"{initials} {last}".strip())
        else:
            out.append(n)
    if len(out) > 6:
        return out[0] + " et al."
    if len(out) <= 2:
        return " and ".join(out)
    return ", ".join(out[:-1]) + ", and " + out[-1]


def fmt(typ, f):
    a = authors(f.get("author", "")) if f.get("author") else ""
    t = clean(f.get("title", ""))
    y = clean(f.get("year", ""))
    doi = clean(f.get("doi", ""))
    parts = []
    if typ == "article":
        s = f'{a}, "{t}," *{clean(f.get("journal", ""))}*'
        if f.get("volume"):
            s += f', vol. {clean(f["volume"])}'
        if f.get("number"):
            s += f', no. {clean(f["number"])}'
        if f.get("pages"):
            s += f', pp. {clean(f["pages"])}'
        elif f.get("eid"):
            s += f', Art. no. {clean(f["eid"])}'
        s += f", {y}"
    elif typ in ("inproceedings", "incollection"):
        s = f'{a}, "{t}," in *{clean(f.get("booktitle", ""))}*'
        if f.get("publisher"):
            s += f', {clean(f["publisher"])}'
        if f.get("pages"):
            s += f', pp. {clean(f["pages"])}'
        s += f", {y}"
    elif typ == "book":
        s = f'{a}, *{t}*. {clean(f.get("address", ""))}: {clean(f.get("publisher", ""))}, {y}'
    elif typ == "techreport":
        num = " ".join(x for x in [clean(f.get("type", "")), clean(f.get("number", ""))] if x)
        s = f'{a}, "{t}," {clean(f.get("institution", ""))}'
        if num:
            s += f", {num}"
        s += f", {y}"
    else:
        bits = []
        if f.get("eprint"):
            bits.append(f'arXiv:{clean(f["eprint"])}')
        if f.get("howpublished"):
            bits.append(clean(f["howpublished"]))
        if y:
            bits.append(y)
        s = f'{a}, "{t}," ' + ", ".join(bits)
        if f.get("note"):
            s += f". {clean(f['note'])}"
    parts.append(s)
    if doi:
        parts.append(f"doi: {doi}")
    if f.get("url") and typ != "misc":
        parts.append(clean(f["url"]))
    return ", ".join(parts) + "."


def main():
    files = sorted(x for x in os.listdir(HERE) if re.match(r"\d\d_.*\.md$", x))
    text = "\n".join(open(os.path.join(HERE, x)).read().rstrip() + "\n" for x in files)
    bib = parse_bib(open(SRC_BIB).read())
    order = []

    def repl(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in keys:
            if k not in bib:
                raise SystemExit(f"missing bib key: {k}")
            if k not in order:
                order.append(k)
            nums.append(order.index(k) + 1)
        return ", ".join(f"[{n}]" for n in nums)

    body = re.sub(r"\[(@[\w]+(?:\s*;\s*@[\w]+)*)\]", repl, text)
    refs = ["## REFERENCES", ""]
    for i, k in enumerate(order, 1):
        typ, f, _ = bib[k]
        refs.append(f"[{i}] {fmt(typ, f)}")
        refs.append("")
    # References go before the appendices (file 11_ and later).
    marker = "## APPENDIX A."
    head, tail = body.split(marker, 1)
    out = head.rstrip() + "\n\n" + "\n".join(refs).rstrip() + "\n\n" + marker + tail
    open(os.path.join(ROOT, "manuscript.md"), "w").write(out)
    with open(os.path.join(ROOT, "references.bib"), "w") as fh:
        fh.write("% Entries cited in manuscript.md, in order of first citation.\n")
        fh.write("% Copied verbatim from research paper/references.bib (verified entries).\n\n")
        for k in order:
            fh.write(bib[k][2].strip() + "\n\n")
    with open(os.path.join(HERE, "citation_order.txt"), "w") as fh:
        for i, k in enumerate(order, 1):
            fh.write(f"[{i}] {k}\n")
    print(f"sections={len(files)} citations={len(order)}")


if __name__ == "__main__":
    main()
