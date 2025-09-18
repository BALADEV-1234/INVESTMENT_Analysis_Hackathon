# Enhanced PyDash Express UI for Multi-Agent Investment Analysis System
import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import base64
import io
import time

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests

# Initialize Dash app with custom theme and CSS
app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP, 
                    dbc.icons.FONT_AWESOME,
                    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
                ],
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

app.title = "AI Investment Analyst"

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Enhanced color scheme
COLORS = {
    'primary': '#1e3a5f',
    'secondary': '#4a90e2',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            }
            .card {
                border: none;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            .btn-primary:hover {
                background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            }
            .badge {
                font-weight: 500;
                padding: 8px 12px;
            }
            .upload-area {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border: 2px dashed #667eea;
                transition: all 0.3s;
            }
            .upload-area:hover {
                background: linear-gradient(135deg, #c3cfe2 0%, #f5f7fa 100%);
                border-color: #764ba2;
            }
            .score-display {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700;
            }
            .nav-tabs .nav-link {
                color: #667eea;
                font-weight: 500;
                border: none;
                border-bottom: 3px solid transparent;
            }
            .nav-tabs .nav-link.active {
                border-bottom: 3px solid #667eea;
                background: none;
            }
            .spinner-border {
                color: #667eea;
            }
            .progress-message {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: shine 3s linear infinite;
            }
            @keyframes shine {
                to { background-position: 200% center; }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App Layout
app.layout = html.Div([
    # Header with animated background
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-3x mb-3", 
                                  style={'color': 'white'}),
                            html.H1("AI Investment Analyst Platform", 
                                   className="display-4 fw-bold text-white mb-3"),
                            html.P("Multi-Agent Startup Evaluation with Web Intelligence", 
                                   className="lead text-white-50"),
                            dbc.Badge("v3.0", color="light", pill=True, className="mt-2")
                        ], className="text-center py-5")
                    ])
                ], width=12)
            ])
        ], fluid=True)
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["gradient_start"]} 0%, {COLORS["gradient_end"]} 100%)',
        'marginBottom': '-50px',
        'paddingBottom': '70px'
    }),
    
    # Main container
    dbc.Container([
        html.Div([
            # Status indicators
            dbc.Row([
                dbc.Col([
                    html.Div(id='system-status', className="mb-4")
                ], width=12)
            ]),
            
            # File Upload Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3([
                                html.I(className="fas fa-upload me-3"),
                                "Upload Startup Materials"
                            ], className="mb-4"),
                            
                            dcc.Upload(
                                id='upload-data',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt fa-4x mb-3", 
                                          style={'color': COLORS['gradient_start']}),
                                    html.H4('Drop files here or click to browse', 
                                           className="mb-2"),
                                    html.P('Supported formats: PDF, PPTX, XLSX, CSV, TXT, MD, JSON', 
                                          className="text-muted mb-0")
                                ], className="text-center py-5"),
                                className='upload-area rounded-3',
                                multiple=True
                            ),
                            
                            # Uploaded files display
                            html.Div(id='uploaded-files', className="mt-4"),
                            
                            # Analysis configuration
                            dbc.Accordion([
                                dbc.AccordionItem([
                                    dbc.Row([
                                        dbc.Col([
                                            html.Label("Analysis Mode", 
                                                      className="fw-bold mb-2"),
                                            dbc.RadioItems(
                                                id='analysis-type',
                                                options=[
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-microscope me-2"),
                                                            "Full Analysis"
                                                        ]), 
                                                        "value": "full"
                                                    },
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-file-alt me-2"),
                                                            "Summary"
                                                        ]), 
                                                        "value": "summary"
                                                    },
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-chart-pie me-2"),
                                                            "Scoring"
                                                        ]), 
                                                        "value": "scoring"
                                                    },
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-question me-2"),
                                                            "Questions"
                                                        ]), 
                                                        "value": "questions"
                                                    }
                                                ],
                                                value='full',
                                                inline=True,
                                                className="custom-radio"
                                            )
                                        ], md=6),
                                        dbc.Col([
                                            html.Label("Enhanced Features", 
                                                      className="fw-bold mb-2"),
                                            dbc.Checklist(
                                                id='analysis-options',
                                                options=[
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-search me-2"),
                                                            "Web Search"
                                                        ]), 
                                                        "value": "web_search"
                                                    },
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-brain me-2"),
                                                            "AI Questions"
                                                        ]), 
                                                        "value": "questions"
                                                    },
                                                    {
                                                        "label": html.Span([
                                                            html.I(className="fas fa-tachometer-alt me-2"),
                                                            "Deep Scoring"
                                                        ]), 
                                                        "value": "scoring"
                                                    }
                                                ],
                                                value=['web_search', 'questions', 'scoring'],
                                                inline=True
                                            )
                                        ], md=6)
                                    ])
                                ], title="⚙️ Advanced Configuration", item_id="config")
                            ], start_collapsed=True, className="mt-4 mb-4"),
                            
                            # Analyze button
                            dbc.Button(
                                [
                                    html.I(className="fas fa-rocket me-2"),
                                    html.Span("Analyze Startup", id="button-text")
                                ],
                                id='analyze-button',
                                color="primary",
                                size="lg",
                                className="w-100",
                                disabled=True
                            ),
                            
                            # Progress indicator
                            html.Div(id='progress-container', className="mt-3")
                        ])
                    ], className="shadow-lg")
                ], width=12)
            ], className="mb-4"),
            
            # Results container
            dcc.Loading(
                id="loading-results",
                type="circle",
                children=[
                    html.Div(id='analysis-results')
                ],
                color=COLORS['gradient_start']
            )
            
        ], className="main-container")
    ], fluid=True),
    
    # Hidden stores
    dcc.Store(id='analysis-data'),
    dcc.Store(id='uploaded-files-store'),
    dcc.Interval(id='progress-interval', interval=1000, disabled=True),
    dcc.Store(id='progress-state', data={'stage': 0, 'message': ''})
    
], style={'background': f'linear-gradient(135deg, {COLORS["gradient_start"]} 0%, {COLORS["gradient_end"]} 100%)'})

# Check system status on load
@app.callback(
    Output('system-status', 'children'),
    Input('system-status', 'id')
)
def check_system_status(_):
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            api_status = data.get('api_keys_status', {})
            
            badges = []
            if api_status.get('google_ai'):
                badges.append(dbc.Badge("Google AI ✓", color="success", pill=True, className="me-2"))
            else:
                badges.append(dbc.Badge("Google AI ✗", color="danger", pill=True, className="me-2"))
                
            if api_status.get('tavily_search'):
                badges.append(dbc.Badge("Web Search ✓", color="success", pill=True, className="me-2"))
            else:
                badges.append(dbc.Badge("Web Search ✗", color="warning", pill=True, className="me-2"))
                
            if api_status.get('langsmith_tracing'):
                badges.append(dbc.Badge("Tracing ✓", color="info", pill=True, className="me-2"))
            
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "System Online | ",
                *badges
            ], color="success", dismissable=True)
    except:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Backend not connected. Please ensure the API server is running on port 8000."
        ], color="danger")

# Handle file uploads
@app.callback(
    [Output('uploaded-files', 'children'),
     Output('analyze-button', 'disabled'),
     Output('uploaded-files-store', 'data')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filenames):
    if not contents:
        return html.Div("No files uploaded yet", className="text-muted text-center mt-3"), True, None
    
    files_info = []
    total_size = 0
    
    for content, filename in zip(contents, filenames):
        content_string = content.split(',')[1]
        decoded = base64.b64decode(content_string)
        file_size = len(decoded)
        total_size += file_size
        
        ext = os.path.splitext(filename)[1].lower()
        
        # Enhanced icon mapping
        icon_map = {
            '.pdf': ('fa-file-pdf', 'danger'),
            '.xlsx': ('fa-file-excel', 'success'),
            '.xls': ('fa-file-excel', 'success'),
            '.csv': ('fa-file-csv', 'success'),
            '.pptx': ('fa-file-powerpoint', 'warning'),
            '.ppt': ('fa-file-powerpoint', 'warning'),
            '.txt': ('fa-file-alt', 'info'),
            '.md': ('fa-markdown', 'info'),
            '.json': ('fa-code', 'secondary')
        }
        
        icon, color = icon_map.get(ext, ('fa-file', 'secondary'))
        
        files_info.append({
            'filename': filename,
            'size': file_size,
            'icon': icon,
            'color': color,
            'content': content,
            'ext': ext
        })
    
    # Create enhanced file display
    file_cards = []
    for info in files_info:
        size_str = f"{info['size']/1024:.1f} KB" if info['size'] < 1024*1024 else f"{info['size']/(1024*1024):.1f} MB"
        
        file_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.I(className=f"fas {info['icon']} fa-2x mb-2", 
                              style={'color': COLORS[info['color']]}),
                        html.P(info['filename'], className="mb-0 small fw-bold"),
                        html.P(size_str, className="mb-0 text-muted small")
                    ], className="text-center p-3")
                ], className="h-100")
            ], md=3, className="mb-3")
        )
    
    files_display = html.Div([
        html.H5([
            html.I(className="fas fa-folder-open me-2"),
            f"Files Ready ({len(files_info)} files, {total_size/(1024*1024):.1f} MB total)"
        ], className="mb-3"),
        dbc.Row(file_cards)
    ])
    
    return files_display, False, files_info

# Perform analysis with progress tracking
@app.callback(
    [Output('analysis-results', 'children'),
     Output('progress-container', 'children'),
     Output('progress-interval', 'disabled'),
     Output('button-text', 'children')],
    Input('analyze-button', 'n_clicks'),
    [State('uploaded-files-store', 'data'),
     State('analysis-type', 'value'),
     State('analysis-options', 'value')],
    prevent_initial_call=True
)
def perform_analysis(n_clicks, files_info, analysis_type, options):
    if not n_clicks or not files_info:
        raise PreventUpdate
    
    # Start progress tracking
    progress_bar = dbc.Progress(
        value=0,
        id="analysis-progress-bar",
        animated=True,
        striped=True,
        color="primary",
        className="mb-2"
    )
    
    progress_display = html.Div([
        progress_bar,
        html.P("Initializing multi-agent system...", 
              className="text-center progress-message")
    ])
    
    # Prepare files
    files_to_upload = []
    for file_info in files_info:
        content_string = file_info['content'].split(',')[1]
        decoded = base64.b64decode(content_string)
        files_to_upload.append(('files', (file_info['filename'], io.BytesIO(decoded))))
    
    # Select endpoint
    endpoint_map = {
        'full': '/analyze',
        'summary': '/summary',
        'scoring': '/scoring',
        'questions': '/questions'
    }
    
    endpoint = endpoint_map.get(analysis_type, '/analyze')
    
    try:
        # Make API request
        response = requests.post(f"{API_URL}{endpoint}", files=files_to_upload, timeout=6000)
        
        if response.status_code == 200:
            data = response.json()
            results = create_comprehensive_results(data, analysis_type)
            return results, None, True, "Analyze Startup"
        else:
            error = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Analysis failed: {response.text}"
            ], color="danger")
            return error, None, True, "Analyze Startup"
            
    except requests.Timeout:
        error = dbc.Alert([
            html.I(className="fas fa-clock me-2"),
            "Analysis timeout. Processing large files may take longer. Please try again."
        ], color="warning")
        return error, None, True, "Analyze Startup"
    except Exception as e:
        error = dbc.Alert([
            html.I(className="fas fa-bug me-2"),
            f"Error: {str(e)}"
        ], color="danger")
        return error, None, True, "Analyze Startup"

def create_comprehensive_results(data, analysis_type):
    """Create enhanced results display."""
    
    components = []
    
    # Success header
    if data.get('status') == 'success':
        processing_time = data.get('metadata', {}).get('processing_time_seconds', 0)
        components.append(
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Analysis completed successfully in {processing_time:.1f} seconds!"
            ], color="success", dismissable=True, className="mb-4")
        )
    
    # Create tabbed interface for results
    tabs = []
    
    # Overview tab with scores
    if 'investment_scores' in data or 'overall_score' in data:
        overview_content = create_enhanced_scores_display(data)
        tabs.append(
            dbc.Tab(
                overview_content, 
                label="📊 Scores",  # Using emoji instead of icon component
                tab_id="scores"
            )
        )
    
    # Executive Summary tab
    if 'investment_summary' in data:
        summary_content = create_enhanced_summary_display(data)
        tabs.append(
            dbc.Tab(
                summary_content, 
                label="📄 Summary",
                tab_id="summary"
            )
        )
    
    # Founder Questions tab
    if 'founder_questions' in data or 'founder_interview_guide' in data:
        questions_content = create_enhanced_questions_display(data)
        tabs.append(
            dbc.Tab(
                questions_content, 
                label="❓ Questions",
                tab_id="questions"
            )
        )
    
    # Agent Analyses tab (for full analysis)
    if 'specialized_analyses' in data:
        analyses_content = create_agent_analyses_display(data)
        tabs.append(
            dbc.Tab(
                analyses_content, 
                label="🤖 Agents",
                tab_id="agents"
            )
        )
    
    # Web Intelligence tab
    if 'web_intelligence' in data and data['web_intelligence'].get('search_performed'):
        web_content = create_web_intelligence_display(data)
        tabs.append(
            dbc.Tab(
                web_content, 
                label="🌐 Web Intel",
                tab_id="web"
            )
        )
    
    if tabs:
        components.append(
            dbc.Card([
                dbc.CardBody([
                    dbc.Tabs(tabs, active_tab=tabs[0].tab_id if tabs else None)
                ])
            ], className="shadow-lg")
        )
    
    # Download report button
    components.append(
        html.Div([
            dbc.Button([
                html.I(className="fas fa-download me-2"),
                "Download Report"
            ], color="secondary", outline=True, className="mt-4")
        ], className="text-center")
    )
    
    return html.Div(components)

def create_enhanced_scores_display(data):
    """Create enhanced investment scores visualization."""
    
    scores = data.get('investment_scores', {}) or data.get('detailed_scores', {})
    overall = data.get('overall_score', scores.get('overall_weighted', 0))
    recommendation = scores.get('recommendation', data.get('recommendation', 'Hold'))
    
    # Determine color and icon based on recommendation
    rec_config = {
        'Strong Buy': ('success', 'fa-rocket', '#28a745'),
        'Buy': ('info', 'fa-thumbs-up', '#17a2b8'),
        'Hold': ('warning', 'fa-pause-circle', '#ffc107'),
        'Pass': ('danger', 'fa-times-circle', '#dc3545')
    }
    
    rec_color, rec_icon, hex_color = rec_config.get(recommendation, ('secondary', 'fa-question', '#6c757d'))
    
    # Create gauge chart for overall score
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall,
        title={'text': "Overall Investment Score"},
        delta={'reference': 60, 'position': "bottom"},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1},
            'bar': {'color': hex_color},
            'steps': [
                {'range': [0, 45], 'color': "#ffebee"},
                {'range': [45, 60], 'color': "#fff3cd"},
                {'range': [60, 75], 'color': "#cfe2ff"},
                {'range': [75, 100], 'color': "#d1f2eb"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 60
            }
        }
    ))
    
    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    
    # Create radar chart for dimensions
    categories = ['Team', 'Market', 'Product', 'Traction', 'Financials', 'Moat']
    values = [
        scores.get('team', 0),
        scores.get('market', 0),
        scores.get('product', 0),
        scores.get('traction', 0),
        scores.get('financials', 0),
        scores.get('moat', 0)
    ]
    
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(size=8, color=hex_color),
        line=dict(color=hex_color, width=2)
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    # Score breakdown cards
    score_cards = []
    weights = scores.get('weights', {})
    
    for key, label in [('team', 'Team'), ('market', 'Market'), ('product', 'Product'), 
                       ('traction', 'Traction'), ('financials', 'Financials'), ('moat', 'Moat')]:
        score_val = scores.get(key, 0)
        weight_val = weights.get(key, 0)
        weighted_contribution = score_val * weight_val
        
        # Color based on score
        if score_val >= 75:
            color = "success"
        elif score_val >= 60:
            color = "info"
        elif score_val >= 45:
            color = "warning"
        else:
            color = "danger"
        
        score_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(label, className="text-muted mb-2"),
                        html.H3(f"{score_val:.0f}", className="mb-1 fw-bold"),
                        dbc.Progress(value=score_val, color=color, className="mb-2", style={'height': '8px'}),
                        html.Small(f"Weight: {weight_val:.0%}", className="text-muted")
                    ])
                ], className="h-100")
            ], md=4, className="mb-3")
        )
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H1(f"{overall:.0f}", className="display-1 mb-0 score-display"),
                            html.P("OVERALL SCORE", className="text-muted mb-3"),
                            dbc.Badge([
                                html.I(className=f"fas {rec_icon} me-2"),
                                recommendation.upper()
                            ], color=rec_color, className="p-3", style={'fontSize': '1.2rem'}),
                            html.Hr(className="my-4"),
                            dcc.Graph(figure=fig_gauge, config={'displayModeBar': False})
                        ], className="text-center")
                    ])
                ])
            ], md=5),
            dbc.Col([
                html.H5("Score Distribution", className="mb-3"),
                dcc.Graph(figure=fig_radar, config={'displayModeBar': False})
            ], md=7)
        ]),
        html.Hr(className="my-4"),
        html.H5("Detailed Scoring Breakdown", className="mb-3"),
        dbc.Row(score_cards),
        
        # Investment recommendation panel
        dbc.Alert([
            html.H5("Investment Recommendation", className="mb-3"),
            html.P([
                "Based on comprehensive multi-agent analysis, this startup receives a ",
                html.Strong(recommendation),
                f" recommendation with an overall score of {overall:.1f}/100."
            ]),
            html.Ul([
                html.Li("Strong Buy: 75+ (High potential unicorn candidate)"),
                html.Li("Buy: 60-74 (Solid investment opportunity)"),
                html.Li("Hold: 45-59 (Needs more validation)"),
                html.Li("Pass: <45 (Significant concerns)")
            ])
        ], color=rec_color, className="mt-4")
    ])

def create_enhanced_summary_display(data):
    """Create enhanced executive summary display."""
    
    summary = data.get('investment_summary', '')
    confidence = data.get('confidence_score', 0)
    
    # Parse summary sections
    sections = []
    current_section = {'title': '', 'content': []}
    
    for line in summary.split('\n'):
        if line.startswith('**') and line.endswith('**'):
            if current_section['content']:
                sections.append(current_section)
            current_section = {
                'title': line.strip('*').strip(),
                'content': []
            }
        elif line.strip():
            current_section['content'].append(line)
    
    if current_section['content']:
        sections.append(current_section)
    
    # Create accordion for sections
    accordion_items = []
    for i, section in enumerate(sections):
        if section['title']:
            content = '\n'.join(section['content'])
            accordion_items.append(
                dbc.AccordionItem(
                    dcc.Markdown(content),
                    title=section['title'],
                    item_id=f"section-{i}"
                )
            )
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.H4("Confidence Score", className="mb-2"),
                            html.H2(f"{confidence:.1%}", className="text-primary mb-0"),
                            dbc.Progress(value=confidence*100, color="primary", className="mt-2")
                        ], className="text-center")
                    ])
                ])
            ], md=3),
            dbc.Col([
                html.H5("Executive Analysis", className="mb-3"),
                dbc.Accordion(accordion_items, start_collapsed=False, flush=True) if accordion_items else dcc.Markdown(summary)
            ], md=9)
        ])
    ])

def create_enhanced_questions_display(data):
    """Create enhanced founder questions display."""
    
    questions = data.get('founder_questions') or data.get('founder_interview_guide', '')
    top_questions = data.get('top_founder_questions', [])
    categories = data.get('question_categories', {})
    gaps = data.get('identified_gaps', '')
    
    components = []
    
    # Gaps identified
    if gaps:
        components.append(
            dbc.Alert([
                html.H5([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Key Information Gaps Identified"
                ], className="mb-3"),
                dcc.Markdown(gaps)
            ], color="warning", className="mb-4")
        )
    
    # Top priority questions
    if top_questions:
        priority_cards = []
        for i, q in enumerate(top_questions[:5], 1):
            priority_cards.append(
                dbc.Card([
                    dbc.CardBody([
                        dbc.Badge(f"Priority {i}", color="danger", className="mb-2"),
                        html.P(q, className="mb-0")
                    ])
                ], className="mb-2")
            )
        
        components.append(
            html.Div([
                html.H5([
                    html.I(className="fas fa-star me-2"),
                    "Must-Ask Questions"
                ], className="mb-3"),
                *priority_cards
            ])
        )
    
    # Question categories
    if categories:
        category_tabs = []
        for cat_key, cat_content in categories.items():
            if cat_content:
                category_tabs.append(
                    dbc.Tab(
                        dcc.Markdown(cat_content),
                        label=cat_key.replace('_', ' ').title(),
                        tab_id=f"q-{cat_key}"
                    )
                )
        
        if category_tabs:
            components.append(
                html.Div([
                    html.H5("Question Categories", className="mb-3 mt-4"),
                    dbc.Tabs(category_tabs)
                ])
            )
    
    # Full questions if no categories
    if not categories and questions:
        components.append(
            dbc.Card([
                dbc.CardBody([
                    dcc.Markdown(questions)
                ])
            ])
        )
    
    return html.Div(components)

def create_agent_analyses_display(data):
    """Create specialized agent analyses display."""
    
    analyses = data.get('specialized_analyses', {})
    
    if not analyses:
        return html.Div("No specialized analyses available")
    
    # Create cards for each agent
    agent_cards = []
    
    agent_info = {
        'pitch_deck': ('fa-presentation', 'primary', 'Pitch Deck Analysis'),
        'data_room': ('fa-database', 'success', 'Financial & Traction'),
        'web_content': ('fa-globe', 'info', 'Web Intelligence'),
        'interaction': ('fa-comments', 'warning', 'Interaction Signals')
    }
    
    for agent, content in analyses.items():
        icon, color, title = agent_info.get(agent, ('fa-robot', 'secondary', agent.title()))
        confidence = content.get('confidence', 0)
        
        agent_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className=f"fas {icon} me-2"),
                        html.Span(title),
                        dbc.Badge(f"{confidence:.0%}", color="light", className="float-end")
                    ], style={'backgroundColor': COLORS[color], 'color': 'white'}),
                    dbc.CardBody([
                        dcc.Markdown(
                            content.get('analysis', '')[:1000] + "..." 
                            if len(content.get('analysis', '')) > 1000 
                            else content.get('analysis', ''),
                            className="small"
                        ),
                        dbc.Button("View Full Analysis", 
                                  color=color, 
                                  outline=True, 
                                  size="sm",
                                  id={'type': 'agent-modal-btn', 'index': agent})
                    ])
                ], className="h-100")
            ], md=6, className="mb-3")
        )
    
    return html.Div([
        html.H5("Specialized Agent Insights", className="mb-3"),
        dbc.Row(agent_cards)
    ])

def create_web_intelligence_display(data):
    """Create web intelligence insights display."""
    
    web_intel = data.get('web_intelligence', {})
    company_info = web_intel.get('company_info', {})
    
    components = []
    
    # Company information card
    if company_info and any(company_info.values()):
        info_items = []
        for key, value in company_info.items():
            if value:
                info_items.append(
                    html.Tr([
                        html.Td(html.Strong(key.replace('_', ' ').title())),
                        html.Td(str(value))
                    ])
                )
        
        components.append(
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-building me-2"),
                    "Company Intelligence"
                ]),
                dbc.CardBody([
                    html.Table([
                        html.Tbody(info_items)
                    ], className="table table-borderless")
                ])
            ], className="mb-3")
        )
    
    # Search status
    if web_intel.get('search_performed'):
        components.append(
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "Enhanced web search completed successfully. ",
                "Competitive intelligence and market validation data integrated into analysis."
            ], color="success")
        )
    else:
        components.append(
            dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "Web search not performed. Enable Tavily API for enhanced intelligence."
            ], color="info")
        )
    
    return html.Div(components)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)