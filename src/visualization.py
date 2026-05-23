import math
import plotly.graph_objects as go

def radial_matrix(base, ranked, n=8):
    selected = ranked[:n]
    xs = [0]
    ys = [0]
    text = [f"{base.get('emoji','')} {base['name']}"]
    sizes = [68]
    colors = ["#020617"]
    edge_x = []
    edge_y = []
    annotations = []
    for i, item in enumerate(selected):
        angle = i / len(selected) * 2 * math.pi - math.pi / 2
        radius = 1.0
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        xs.append(x)
        ys.append(y)
        text.append(f"{item.get('emoji','')} {item['name']}<br>Score {round(item['total']*100)}<br>{item['category']}")
        sizes.append(34 + item["total"] * 25)
        colors.append("#f59e0b" if item["contrast"] > item["molecular"] else "#0f766e")
        edge_x += [0, x, None]
        edge_y += [0, y, None]
        annotations.append(dict(x=x*1.18, y=y*1.18, text=f"{item.get('emoji','')}<br><b>{item['name']}</b><br>{round(item['total']*100)}", showarrow=False, font=dict(size=12, color="#0f172a"), bgcolor="rgba(255,255,255,0.88)", bordercolor="#e2e8f0", borderpad=5))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1.2, color="rgba(15,23,42,0.22)"), hoverinfo="none", showlegend=False))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", marker=dict(size=sizes, color=colors, line=dict(width=2, color="white")), text=[text[0]] + [""] * len(selected), textfont=dict(color="white", size=15), hovertext=text, hoverinfo="text", showlegend=False))
    fig.update_layout(height=620, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="#fffbeb", paper_bgcolor="#fffbeb", xaxis=dict(visible=False, range=[-1.55, 1.55]), yaxis=dict(visible=False, range=[-1.40, 1.40], scaleanchor="x", scaleratio=1), annotations=annotations)
    return fig
