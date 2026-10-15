"""Build a HyperFrames scene from the worked example: keep the ENGINE sections, swap the CONTENT."""
import json, re
EX = open("/Users/itsaibarr/conductor/workspaces/learning-system/paper-teaching/skills/teach-understanding/references/hyperframes-example.html").read()


def build(narration, content_js, titles, ntitles, motion_js, basis, css="", ground=False):
    s = EX
    if not ground:
        s = s.replace('        <div id="ground" class="abs"></div>\n', "")
    s = re.sub(r'<script type="application/json" id="narration">.*?</script>',
               lambda m: '<script type="application/json" id="narration">' + json.dumps(narration) + "</script>", s, flags=re.S)
    s = re.sub(r'(<div id="basis"[^>]*>).*?(</div>)', lambda m: m.group(1) + basis + m.group(2), s, count=1, flags=re.S)
    s = s.replace('        <div id="axis" class="abs"></div>\n', "")
    a = s.index("      // ===== CONTENT (rewrite for your topic): axis, items, captions =====")
    b = s.index("      // ===== ENGINE (keep as is): the beat loop.")
    s = s[:a] + "      // ===== CONTENT (rewrite for your topic): items, captions =====\n" + content_js + "\n" + s[b:]
    a = s.index('      [["Part 1: the attack"')
    b = s.index("      // ===== CONTENT: motion inside beats")
    t = "      " + titles + ".forEach(([txt, a, b], i) => {\n" \
        '        const el = item("title" + i, "cap", "t", "title", {}, txt);\n' \
        '        tl.to(el, { opacity: 1, duration: 0.3 }, a);\n        if (i < %d) tl.to(el, { opacity: 0, duration: 0.2 }, b);\n      });\n' % (ntitles - 1)
    s = s[:a] + "__TITLES__\n" + s[b:]
    s = s.replace("__TITLES__", t)
    a = s.index("      // ===== CONTENT: motion inside beats")
    b = s.index('      window.__timelines["main"] = tl;')
    s = s[:a] + "      // ===== CONTENT: motion inside beats =====\n" + motion_js + "\n\n" + s[b:]
    s = s.replace("    </style>", css + "\n    </style>", 1)
    return s
