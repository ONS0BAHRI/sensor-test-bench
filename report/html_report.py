"""Rapport HTML autonome (images intégrées) : un seul fichier à ouvrir, envoyer ou archiver."""
from __future__ import annotations

import base64
import html
from pathlib import Path

CSS = """
:root { --ink:#1d2330; --muted:#5d6675; --line:#e3e6ec; --ok:#2e9e5b; --ko:#d64545; --bg:#f7f8fa; }
* { box-sizing: border-box; }
body { margin:0; font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif; color:var(--ink); background:var(--bg); }
main { max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }
h1 { font-size: 26px; margin: 0 0 4px; }
.meta { color: var(--muted); font-size: 14px; }
.banner { margin: 24px 0; padding: 18px 22px; border-radius: 10px; color: #fff; font-size: 22px; font-weight: 700; }
.banner.ok { background: var(--ok); } .banner.ko { background: var(--ko); }
.banner small { display:block; font-size: 14px; font-weight: 500; opacity: .9; }
table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; font-size: 14px; }
th { background: #eef1f5; font-weight: 600; }
.v { font-weight: 700; } .v.OK { color: var(--ok); } .v.KO { color: var(--ko); }
section.test { background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px 20px; margin-top:20px; }
section.test h2 { font-size: 18px; margin: 0 0 6px; }
section.test img { max-width: 100%; height: auto; margin-top: 12px; }
dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; margin: 10px 0 0; font-size: 14px; }
dt { color: var(--muted); } dd { margin: 0; font-variant-numeric: tabular-nums; }
"""


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _img(path: Path | None) -> str:
    if not path or not Path(path).exists():
        return ""
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return f'<img alt="graphique" src="data:image/png;base64,{data}">'


def write_html_report(path: Path, meta: dict, results: list, figures: dict) -> Path:
    failed = [r for r in results if not r.passed]
    ok = not failed
    rows = "".join(
        f"<tr><td>{r.test_id}</td><td><a href='#{r.test_id}'>{html.escape(r.title)}</a></td>"
        f"<td class='v {r.verdict}'>{r.verdict}</td><td>{html.escape(r.criterion)}</td></tr>"
        for r in results)
    sections = []
    for r in results:
        measures = "".join(f"<dt>{html.escape(str(k))}</dt><dd>{html.escape(_fmt(v))}</dd>"
                           for k, v in r.measures.items())
        notes = f"<p class='meta'>{html.escape(r.notes)}</p>" if r.notes else ""
        sections.append(
            f"<section class='test' id='{r.test_id}'><h2>{r.test_id} · {html.escape(r.title)} "
            f"<span class='v {r.verdict}'>{r.verdict}</span></h2>"
            f"<div class='meta'>Critère : {html.escape(r.criterion)}</div><dl>{measures}</dl>{notes}"
            f"{_img(figures.get(r.test_id))}</section>")
    verdict = "CAPTEUR CONFORME" if ok else "CAPTEUR NON CONFORME"
    detail = (f"{len(results)} tests sur {len(results)} réussis" if ok
              else f"{len(failed)} test(s) en échec : " + ", ".join(r.test_id for r in failed))
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rapport {html.escape(meta['run_id'])}</title><style>{CSS}</style></head><body><main>
<h1>Rapport de campagne de test · capteur {html.escape(meta['serial_number'])}</h1>
<div class="meta">Campagne {html.escape(meta['run_id'])} · {html.escape(meta['started_at'])} ·
mode {html.escape(meta['mode'].upper())} · firmware {html.escape(meta['firmware'])} ·
durée {meta['duration_s']:.1f} s · commit {html.escape(meta['git_commit'])}</div>
<div class="banner {'ok' if ok else 'ko'}">{verdict}<small>{detail}</small></div>
<table><thead><tr><th>ID</th><th>Test</th><th>Verdict</th><th>Critère</th></tr></thead>
<tbody>{rows}</tbody></table>
{''.join(sections)}
</main></body></html>"""
    path.write_text(page, encoding="utf-8")
    return path
