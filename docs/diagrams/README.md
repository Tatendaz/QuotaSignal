# Quota flow diagram

`quota-flow.json` is the Archify architecture source. The SVG files are the auto-theme export and fixed light/dark variants. The README uses the fixed variants in a `<picture>` element.

Requires the [Archify skill](https://github.com/tt-a1i/archify) and Node.js. From this repository:

```bash
node /path/to/archify/bin/archify.mjs validate architecture docs/diagrams/quota-flow.json --quality showcase --json
node /path/to/archify/bin/archify.mjs deliver architecture docs/diagrams/quota-flow.json /tmp/quotasignal-architecture.html --quality showcase --json
node /path/to/archify/bin/archify.mjs visual-check /tmp/quotasignal-architecture.html --json
```

Open the delivered viewer and choose Export → SVG. Save as `quota-flow.svg`. For the fixed variants, remove the `prefers-color-scheme: light` media rule and set the root SVG's `data-theme` to `light` or `dark`.

Validation passed all 9 showcase checks with 0 errors and 0 warnings. Browser containment passed at 1440×900, 1600×1000, 1920×1080, and 2048×1320. The rendered light/dark screenshots were inspected. Viewer HTML and visual-check sidecars are not committed.

Evidence sources: `src/quotasignal/protocol.py`, `core.py`, `notify.py`, and `tray.py`. No external service URL is inferred by this diagram: the app requests quota from the local Codex CLI.
