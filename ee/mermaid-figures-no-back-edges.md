---
name: mermaid-figures-no-back-edges
description: In research paper mermaid figures, every edge must run one way from the hub node; no nodes on the hub's input side
metadata:
  type: feedback
---

In the `research paper/` mermaid figures, draw every edge leaving the hub node in
one direction so all peripherals sit on the same side of it (for `flowchart LR`,
the right). Never leave a reverse edge such as `SENSOR -- "echo" --> UNO`, and
declare all nodes before the edge list instead of creating them inline.

**Why:** a reverse edge makes dagre place that node on the opposite side of the
hub and route a long curve back, which is what the user calls the figure looking
"like a net". The user has asked for this twice (Figure 3, then Figure 5).

**How to apply:** for a genuinely two-way link use the bidirectional form
`UNO <-- "D7 trigger out, D8 echo in" --> US`. For a pin that is only an input,
still point the arrow away from the hub and put the direction in the label
(`UNO -- "A3 analog in" --> MQ`), then say in the caption that lines show which
pin serves which device. Check the direction wording against the pin-map table
before writing it. Figure 1 is the reference for a well-organised layout.
Related: [[research-paper-ascii-only]].
