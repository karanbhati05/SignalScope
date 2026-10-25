import json, html
from pathlib import Path
import numpy as np

def save_report(out, title, metrics, sections):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    cards = ''.join(f'<article><small>{html.escape(k)}</small><strong>{html.escape(str(v))}</strong></article>' for k,v in metrics.items())
    body = ''.join(f'<section><h2>{html.escape(k)}</h2>{v}</section>' for k,v in sections)
    (out / 'report.html').write_text('<!doctype html><html><head><meta charset="utf-8"><title>'+html.escape(title)+'</title><style>body{font:16px system-ui;background:#101827;color:#e8edf5;margin:40px auto;max-width:1100px;padding:24px}h1{font-size:38px}h2{color:#73dec9}small{display:block;color:#aabbd1}strong{font-size:24px}article{background:#203047;padding:20px;border-radius:12px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}section{margin-top:32px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #3a4960;text-align:left}svg{width:100%;background:#182539;border-radius:12px}p{line-height:1.6}</style></head><body><h1>'+html.escape(title)+'</h1><p>Reproducible portfolio demonstration. Sample data is simulated; results are not evidence of real business impact.</p><div class="cards">'+cards+'</div>'+body+'</body></html>', encoding='utf-8')

def table(headers, rows):
    return '<table><tr>'+''.join('<th>'+html.escape(str(x))+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'

def lines(series):
    values = np.concatenate([np.asarray(v) for v in series.values()]); lo, hi = values.min(), values.max()
    colors=['#73dec9','#ffbc70','#9bafff']
    result='<svg viewBox="0 0 1000 300" role="img" aria-label="Comparison of time series"><text x="20" y="24" fill="white">'+html.escape(' | '.join(series))+'</text>'
    for (name, vals),color in zip(series.items(),colors):
        pts=' '.join(f'{30+i*940/max(len(vals)-1,1):.1f},{260-(v-lo)*210/max(hi-lo,1e-9):.1f}' for i,v in enumerate(vals))
        result+=f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{pts}"/>'
    return result+'</svg>'
