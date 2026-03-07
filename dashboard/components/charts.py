"""
Chart Components — Smart Agriculture Dashboard
===================================================
Professional Plotly chart builders with dark theme styling.
"""

import plotly.graph_objects as go
import plotly.express as px


# ── Shared Dark Theme Layout ──────────────────────────────────
DARK_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color='#8b9a92', size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    hoverlabel=dict(
        bgcolor='#0d1512',
        font_size=12,
        font_family='Inter',
        bordercolor='#00ff88',
    ),
)


def confidence_bar_chart(names, values, title="Top Predictions"):
    """
    Create a horizontal bar chart for top-K predictions.
    
    Parameters
    ----------
    names : list[str]
        Prediction class names.
    values : list[float]
        Confidence percentages.
    title : str
        Chart title.
    """
    # Clean names
    display_names = []
    for n in names:
        clean = n.replace('___', ' — ').replace('_', ' ')
        if len(clean) > 30:
            clean = clean[:27] + '...'
        display_names.append(clean)
    
    # Reverse for horizontal bar (top at top)
    display_names = display_names[::-1]
    values = values[::-1]
    
    colors = []
    for v in values:
        if v >= 50:
            colors.append('#00ff88')
        elif v >= 20:
            colors.append('#00d4ff')
        elif v >= 5:
            colors.append('#feca57')
        else:
            colors.append('#4a5a52')
    
    fig = go.Figure(go.Bar(
        y=display_names,
        x=values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
        textfont=dict(color='#8b9a92', size=11),
        hovertemplate='%{y}<br>Confidence: %{x:.1f}%<extra></extra>',
    ))
    
    x_max = max(values) if values else 1.0
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text=title, font=dict(size=14, color='#f0f4f2', family='Poppins')),
        xaxis=dict(
            range=[0, max(1.0, x_max * 1.3)],
            showgrid=True,
            gridcolor='rgba(0,255,136,0.05)',
            zeroline=False,
            ticksuffix='%',
        ),
        yaxis=dict(showgrid=False),
        height=max(220, len(names) * 45 + 60),
        bargap=0.3,
    )
    
    return fig


def soil_radar_chart(N, P, K, temperature, humidity, ph, rainfall):
    """
    Create a radar/spider chart showing the soil & environment profile.
    
    All values are normalized to 0-100 scale for visual comparison.
    """
    # Normalize values to 0-100 scale
    categories = ['Nitrogen', 'Phosphorus', 'Potassium', 
                  'Temperature', 'Humidity', 'pH', 'Rainfall']
    
    # Normalization: map to rough 0-100 range
    normalized = [
        min(100, (N / 140) * 100),
        min(100, (P / 140) * 100),
        min(100, (K / 200) * 100),
        min(100, (temperature / 45) * 100),
        humidity,  # already 0-100
        min(100, (ph / 14) * 100),
        min(100, (rainfall / 300) * 100),
    ]
    
    # Close the radar
    categories = categories + [categories[0]]
    normalized = normalized + [normalized[0]]
    
    fig = go.Figure()
    
    # Add fill
    fig.add_trace(go.Scatterpolar(
        r=normalized,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0,255,136,0.1)',
        line=dict(color='#00ff88', width=2),
        marker=dict(size=6, color='#00ff88'),
        name='Soil Profile',
        hovertemplate='%{theta}: %{r:.0f}<extra></extra>',
    ))
    
    # Add ideal range (reference)
    ideal = [55, 40, 50, 55, 65, 48, 60]
    ideal = ideal + [ideal[0]]
    fig.add_trace(go.Scatterpolar(
        r=ideal,
        theta=categories,
        line=dict(color='rgba(0,212,255,0.4)', width=1, dash='dot'),
        name='Ideal Range',
        hovertemplate='%{theta}: %{r:.0f} (ideal)<extra></extra>',
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text='Soil & Environment Profile', 
                   font=dict(size=14, color='#f0f4f2', family='Poppins')),
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=True,
                tickfont=dict(size=9, color='#4a5a52'),
                gridcolor='rgba(0,255,136,0.06)',
            ),
            angularaxis=dict(
                gridcolor='rgba(0,255,136,0.08)',
                linecolor='rgba(0,255,136,0.08)',
                tickfont=dict(size=11, color='#8b9a92'),
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=10, color='#8b9a92'),
            bgcolor='rgba(0,0,0,0)',
        ),
        height=420,
    )
    
    return fig


def yield_gauge(value, title="Predicted Yield"):
    """
    Create an animated gauge meter for yield prediction.
    """
    # Determine thresholds and colors
    if value < 1000:
        color = '#ff4757'
        level = 'Low'
    elif value > 3000:
        color = '#00ff88'
        level = 'High'
    else:
        color = '#feca57'
        level = 'Medium'
    
    max_val = max(5000, value * 1.5)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        number=dict(
            font=dict(size=36, color='#f0f4f2', family='Poppins'),
            valueformat=',.0f',
        ),
        title=dict(
            text=f'{title}<br><span style="font-size:0.8rem;color:{color}">{level} Yield</span>',
            font=dict(size=14, color='#8b9a92', family='Inter'),
        ),
        gauge=dict(
            axis=dict(
                range=[0, max_val],
                tickwidth=1,
                tickcolor='#4a5a52',
                tickfont=dict(size=10, color='#4a5a52'),
            ),
            bar=dict(color=color, thickness=0.7),
            bgcolor='rgba(0,0,0,0)',
            borderwidth=0,
            steps=[
                dict(range=[0, 1000], color='rgba(255,71,87,0.08)'),
                dict(range=[1000, 3000], color='rgba(254,202,87,0.08)'),
                dict(range=[3000, max_val], color='rgba(0,255,136,0.08)'),
            ],
            threshold=dict(
                line=dict(color='#00d4ff', width=3),
                thickness=0.8,
                value=value,
            ),
        ),
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        height=300,
        margin=dict(l=30, r=30, t=60, b=10),
    )
    
    return fig


def soil_breakdown_chart(breakdown):
    """
    Create a horizontal bar chart showing soil quality score breakdown.
    
    Parameters
    ----------
    breakdown : dict
        Factor name -> (actual, max) tuples.
    """
    factors = []
    actuals = []
    maxes = []
    percentages = []
    
    for factor, val in breakdown.items():
        if isinstance(val, tuple):
            actual, maximum = val
        else:
            actual, maximum = val, 25
        factors.append(factor)
        actuals.append(actual)
        maxes.append(maximum)
        percentages.append((actual / maximum * 100) if maximum > 0 else 0)
    
    # Colors based on percentage
    colors = []
    for p in percentages:
        if p >= 75:
            colors.append('#00ff88')
        elif p >= 50:
            colors.append('#00d4ff')
        elif p >= 25:
            colors.append('#feca57')
        else:
            colors.append('#ff4757')
    
    factors = factors[::-1]
    actuals = actuals[::-1]
    maxes = maxes[::-1]
    percentages = percentages[::-1]
    colors = colors[::-1]
    
    fig = go.Figure()
    
    # Background (max) bars
    fig.add_trace(go.Bar(
        y=factors,
        x=maxes,
        orientation='h',
        marker=dict(color='rgba(255,255,255,0.04)', cornerradius=4),
        showlegend=False,
        hoverinfo='skip',
    ))
    
    # Actual score bars
    fig.add_trace(go.Bar(
        y=factors,
        x=actuals,
        orientation='h',
        marker=dict(color=colors, cornerradius=4),
        text=[f'{a:.1f}/{m}' for a, m in zip(actuals[::-1], maxes[::-1])][::-1],
        textposition='outside',
        textfont=dict(color='#8b9a92', size=10),
        showlegend=False,
        hovertemplate='%{y}: %{x:.1f}<extra></extra>',
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text='Soil Quality Breakdown', 
                   font=dict(size=14, color='#f0f4f2', family='Poppins')),
        barmode='overlay',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False),
        height=max(250, len(factors) * 38 + 60),
        bargap=0.35,
    )
    
    return fig


def crop_probability_chart(crops, probabilities):
    """
    Create a styled donut chart for crop probabilities.
    """
    colors = ['#00ff88', '#00d4ff', '#a855f7', '#feca57', '#ff9f43',
              '#ff4757', '#5f27cd', '#48dbfb', '#1dd1a1', '#ee5a24']
    
    fig = go.Figure(go.Pie(
        labels=crops,
        values=probabilities,
        hole=0.55,
        marker=dict(
            colors=colors[:len(crops)],
            line=dict(color='#060b09', width=2),
        ),
        textinfo='label+percent',
        textfont=dict(size=11, color='#f0f4f2', family='Inter'),
        hovertemplate='%{label}<br>%{percent}<extra></extra>',
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text='Crop Distribution', 
                   font=dict(size=14, color='#f0f4f2', family='Poppins')),
        showlegend=True,
        legend=dict(
            font=dict(size=10, color='#8b9a92'),
            bgcolor='rgba(0,0,0,0)',
        ),
        height=380,
        annotations=[dict(
            text='Top<br>Crops',
            x=0.5, y=0.5,
            font=dict(size=14, color='#4a5a52', family='Poppins'),
            showarrow=False,
        )],
    )
    
    return fig


def yield_trend_chart(years, yields, area="", crop=""):
    """
    Create a trend line chart showing yield predictions over years.
    """
    fig = go.Figure()
    
    # Area fill
    fig.add_trace(go.Scatter(
        x=years, y=yields,
        fill='tozeroy',
        fillcolor='rgba(0,255,136,0.06)',
        line=dict(color='#00ff88', width=2.5),
        mode='lines+markers',
        marker=dict(size=6, color='#00ff88',
                    line=dict(width=2, color='#060b09')),
        name='Predicted Yield',
        hovertemplate='Year: %{x}<br>Yield: %{y:,.0f}<extra></extra>',
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(
            text=f'Yield Trend — {crop} in {area}' if crop and area else 'Yield Predictions',
            font=dict(size=14, color='#f0f4f2', family='Poppins'),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,255,136,0.05)',
            title='Year',
            titlefont=dict(color='#4a5a52'),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,255,136,0.05)',
            title='Predicted Yield',
            titlefont=dict(color='#4a5a52'),
        ),
        height=350,
    )
    
    return fig


def health_components_chart(components):
    """
    Create a horizontal bar chart for health component scores.
    """
    names = list(components.keys())
    scores = list(components.values())
    
    colors = []
    for s in scores:
        if s >= 70:
            colors.append('#00ff88')
        elif s >= 50:
            colors.append('#feca57')
        else:
            colors.append('#ff4757')
    
    fig = go.Figure(go.Bar(
        y=names[::-1],
        x=scores[::-1],
        orientation='h',
        marker=dict(
            color=colors[::-1],
            cornerradius=6,
        ),
        text=[f'{s:.0f}/100' for s in scores[::-1]],
        textposition='outside',
        textfont=dict(color='#8b9a92', size=11),
    ))
    
    fig.update_layout(
        **DARK_LAYOUT,
        title=dict(text='Health Components',
                   font=dict(size=14, color='#f0f4f2', family='Poppins')),
        xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False),
        height=220,
        bargap=0.4,
    )
    
    return fig
