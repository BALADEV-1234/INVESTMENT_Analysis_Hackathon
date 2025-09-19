# Professional Investment Analysis Dashboard
import os
import json
import base64
import io
from datetime import datetime
from typing import List, Dict, Any

import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests

# Initialize Dash app with professional theme
app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP, 
                    dbc.icons.FONT_AWESOME,
                    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
                    "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
                ],
                suppress_callback_exceptions=True,
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

app.title = "Investment Analysis Platform"

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Professional color palette
COLORS = {
    'background': '#0A0E27',      # Deep blue-black
    'surface': '#1A1F3A',          # Dark blue surface
    'surface_light': '#262B47',    # Lighter surface
    'primary': '#4C7BF4',          # Bright blue
    'primary_dark': '#2E5CE6',     # Darker blue
    'success': '#00D9A3',          # Teal green
    'warning': '#FFB547',          # Warm orange
    'danger': '#FF5E5B',           # Coral red
    'info': '#00B4D8',             # Cyan
    'text_primary': '#FFFFFF',     # White
    'text_secondary': '#B8BCC8',   # Light gray
    'text_muted': '#6C7293',       # Muted gray
    'border': '#2D3254',           # Border color
    'gradient_1': '#4C7BF4',       # Gradient start
    'gradient_2': '#00D9A3',       # Gradient end
}

# Custom CSS for professional design
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #0A0E27;
                color: #FFFFFF;
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            
            .main-container {
                min-height: 100vh;
                background: #0A0E27;
            }
            
            .glass-card {
                background: rgba(26, 31, 58, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                transition: all 0.3s ease;
            }
            
            .glass-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(76, 123, 244, 0.3);
                border-color: rgba(76, 123, 244, 0.3);
            }
            
            .card {
                background: #1A1F3A;
                border: 1px solid #2D3254;
                border-radius: 12px;
                color: #FFFFFF;
            }
            
            .card-header {
                background: linear-gradient(135deg, #262B47 0%, #1A1F3A 100%);
                border-bottom: 1px solid #2D3254;
                color: #FFFFFF;
                font-weight: 600;
                padding: 1.25rem;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #4C7BF4 0%, #2E5CE6 100%);
                border: none;
                border-radius: 8px;
                font-weight: 600;
                padding: 12px 24px;
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-size: 14px;
            }
            
            .btn-primary:hover {
                background: linear-gradient(135deg, #2E5CE6 0%, #4C7BF4 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(76, 123, 244, 0.4);
            }
            
            .btn-secondary {
                background: transparent;
                border: 2px solid #4C7BF4;
                color: #4C7BF4;
                border-radius: 8px;
                font-weight: 600;
                padding: 10px 22px;
                transition: all 0.3s ease;
            }
            
            .btn-secondary:hover {
                background: #4C7BF4;
                color: #FFFFFF;
                box-shadow: 0 4px 12px rgba(76, 123, 244, 0.3);
            }
            
            .upload-area {
                background: linear-gradient(135deg, rgba(76, 123, 244, 0.1) 0%, rgba(0, 217, 163, 0.1) 100%);
                border: 2px dashed #4C7BF4;
                border-radius: 12px;
                padding: 3rem;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .upload-area:hover {
                background: linear-gradient(135deg, rgba(76, 123, 244, 0.2) 0%, rgba(0, 217, 163, 0.2) 100%);
                border-color: #00D9A3;
                transform: scale(1.02);
            }
            
            .nav-tabs {
                border-bottom: 1px solid #2D3254;
            }
            
            .nav-tabs .nav-link {
                color: #B8BCC8;
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                border-radius: 0;
                font-weight: 500;
                padding: 12px 20px;
                transition: all 0.3s ease;
            }
            
            .nav-tabs .nav-link:hover {
                color: #4C7BF4;
                border-bottom-color: rgba(76, 123, 244, 0.5);
            }
            
            .nav-tabs .nav-link.active {
                color: #FFFFFF;
                background: transparent;
                border-bottom-color: #4C7BF4;
            }
            
            .badge {
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            
            .badge-success {
                background: linear-gradient(135deg, #00D9A3 0%, #00B88C 100%);
                color: #FFFFFF;
            }
            
            .badge-warning {
                background: linear-gradient(135deg, #FFB547 0%, #FF9500 100%);
                color: #FFFFFF;
            }
            
            .badge-danger {
                background: linear-gradient(135deg, #FF5E5B 0%, #FF3B38 100%);
                color: #FFFFFF;
            }
            
            .badge-info {
                background: linear-gradient(135deg, #00B4D8 0%, #0096C7 100%);
                color: #FFFFFF;
            }
            
            .progress {
                background-color: #262B47;
                border-radius: 8px;
                height: 10px;
                overflow: hidden;
            }
            
            .progress-bar {
                background: linear-gradient(90deg, #4C7BF4 0%, #00D9A3 100%);
                transition: width 0.6s ease;
            }
            
            .alert {
                border: none;
                border-radius: 12px;
                padding: 16px 20px;
                font-weight: 500;
            }
            
            .alert-success {
                background: linear-gradient(135deg, rgba(0, 217, 163, 0.2) 0%, rgba(0, 217, 163, 0.1) 100%);
                border-left: 4px solid #00D9A3;
                color: #00D9A3;
            }
            
            .alert-warning {
                background: linear-gradient(135deg, rgba(255, 181, 71, 0.2) 0%, rgba(255, 181, 71, 0.1) 100%);
                border-left: 4px solid #FFB547;
                color: #FFB547;
            }
            
            .alert-danger {
                background: linear-gradient(135deg, rgba(255, 94, 91, 0.2) 0%, rgba(255, 94, 91, 0.1) 100%);
                border-left: 4px solid #FF5E5B;
                color: #FF5E5B;
            }
            
            .alert-info {
                background: linear-gradient(135deg, rgba(0, 180, 216, 0.2) 0%, rgba(0, 180, 216, 0.1) 100%);
                border-left: 4px solid #00B4D8;
                color: #00B4D8;
            }
            
            input, select, textarea {
                background: #262B47 !important;
                border: 1px solid #2D3254 !important;
                color: #FFFFFF !important;
                border-radius: 8px !important;
            }
            
            input:focus, select:focus, textarea:focus {
                border-color: #4C7BF4 !important;
                box-shadow: 0 0 0 3px rgba(76, 123, 244, 0.2) !important;
            }
            
            .custom-radio .form-check-input:checked {
                background-color: #4C7BF4;
                border-color: #4C7BF4;
            }
            
            .form-check-label {
                color: #B8BCC8;
                margin-left: 8px;
            }
            
            .dash-table-container {
                background: #1A1F3A;
                border-radius: 12px;
                overflow: hidden;
            }
            
            .dash-table-container .dash-spreadsheet {
                background: transparent;
            }
            
            .dash-table-container .dash-spreadsheet-container {
                background: transparent;
            }
            
            .dash-table-container td {
                background: #1A1F3A;
                color: #B8BCC8;
                border-color: #2D3254 !important;
            }
            
            .dash-table-container th {
                background: #262B47;
                color: #FFFFFF;
                font-weight: 600;
                border-color: #2D3254 !important;
            }
            
            .score-badge {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 14px;
                letter-spacing: 0.5px;
                text-transform: uppercase;
            }
            
            .score-excellent {
                background: linear-gradient(135deg, #00D9A3 0%, #00B88C 100%);
                color: #FFFFFF;
            }
            
            .score-good {
                background: linear-gradient(135deg, #00B4D8 0%, #0096C7 100%);
                color: #FFFFFF;
            }
            
            .score-moderate {
                background: linear-gradient(135deg, #FFB547 0%, #FF9500 100%);
                color: #FFFFFF;
            }
            
            .score-poor {
                background: linear-gradient(135deg, #FF5E5B 0%, #FF3B38 100%);
                color: #FFFFFF;
            }
            
            .metric-card {
                background: #1A1F3A;
                border: 1px solid #2D3254;
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                border-color: #4C7BF4;
                box-shadow: 0 8px 24px rgba(76, 123, 244, 0.2);
            }
            
            .metric-value {
                font-size: 36px;
                font-weight: 700;
                background: linear-gradient(135deg, #4C7BF4 0%, #00D9A3 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 8px;
            }
            
            .metric-label {
                color: #6C7293;
                font-size: 14px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1A1F3A;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #4C7BF4;
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #2E5CE6;
            }
            
            .markdown-content h1, .markdown-content h2, .markdown-content h3, 
            .markdown-content h4, .markdown-content h5, .markdown-content h6 {
                color: #4C7BF4 !important;
                margin-top: 20px;
                margin-bottom: 12px;
            }
            
            .markdown-content strong, .markdown-content b {
                color: #FFFFFF !important;
                font-weight: 600 !important;
            }
            
            .markdown-content em, .markdown-content i {
                color: #00D9A3 !important;
                font-style: italic !important;
            }
            
            .markdown-content ul, .markdown-content ol {
                color: #B8BCC8 !important;
                margin-left: 20px;
                margin-bottom: 16px;
            }
            
            .markdown-content li {
                margin-bottom: 8px;
                line-height: 1.6;
            }
            
            .markdown-content p {
                color: #B8BCC8 !important;
                line-height: 1.8;
                margin-bottom: 12px;
            }
            
            .markdown-content code {
                background: #262B47 !important;
                color: #4C7BF4 !important;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
            
            .markdown-content blockquote {
                border-left: 4px solid #4C7BF4;
                padding-left: 16px;
                margin: 16px 0;
                color: #B8BCC8 !important;
                font-style: italic;
            }
            
            .markdown-content hr {
                border: none;
                border-top: 1px solid #2D3254;
                margin: 20px 0;
            }
            
            .markdown-content a {
                color: #00B4D8 !important;
                text-decoration: none;
            }
            
            .markdown-content a:hover {
                color: #4C7BF4 !important;
                text-decoration: underline;
            }
            
            .markdown-content table {
                width: 100%;
                border-collapse: collapse;
                margin: 16px 0;
            }
            
            .markdown-content th {
                background: #262B47;
                color: #FFFFFF;
                padding: 12px;
                text-align: left;
                border: 1px solid #2D3254;
            }
            
            .markdown-content td {
                padding: 10px;
                border: 1px solid #2D3254;
                color: #B8BCC8;
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
    # Navigation Header
    html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.H2("AI Investment Analyst", 
                                   style={'color': '#FFFFFF', 'fontWeight': '700', 'marginBottom': '4px'}),
                            html.P("Comprehensive Multi-Agent Startup Evaluation Platform", 
                                   style={'color': '#B8BCC8', 'marginBottom': '0', 'fontSize': '14px'})
                        ], style={'display': 'flex', 'flexDirection': 'column'})
                    ], style={'padding': '20px 0'})
                ], width=8),
                dbc.Col([
                    html.Div([
                        html.Div(id='system-status', style={'textAlign': 'right', 'paddingTop': '25px'})
                    ])
                ], width=4)
            ])
        ], fluid=True)
    ], style={
        'background': 'linear-gradient(180deg, #1A1F3A 0%, #0A0E27 100%)',
        'borderBottom': '1px solid #2D3254',
        'marginBottom': '30px'
    }),
    
    # Main Content
    dbc.Container([
        # File Upload Section
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H4("Upload Documents", 
                               style={'color': '#FFFFFF', 'fontWeight': '600', 'marginBottom': '20px'}),
                        
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt", 
                                      style={'fontSize': '48px', 'color': '#4C7BF4', 'marginBottom': '16px'}),
                                html.H5('Drag & Drop Files Here', 
                                       style={'color': '#FFFFFF', 'marginBottom': '8px', 'fontWeight': '600'}),
                                html.P('or click to browse', 
                                      style={'color': '#B8BCC8', 'marginBottom': '16px'}),
                                html.Div([
                                    html.Span('Supported: ', style={'color': '#6C7293'}),
                                    html.Span('PDF • XLSX • PPTX • CSV • TXT • JSON', 
                                             style={'color': '#4C7BF4', 'fontWeight': '500'})
                                ])
                            ], className='upload-area text-center'),
                            multiple=True
                        ),
                        
                        html.Div(id='uploaded-files', className='mt-4'),
                        
                        # Analysis Configuration
                        html.Div([
                            html.H5("Configuration", 
                                   style={'color': '#FFFFFF', 'fontWeight': '600', 'marginBottom': '16px', 'marginTop': '24px'}),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Analysis Type", 
                                              style={'color': '#B8BCC8', 'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '12px'}),
                                    dbc.RadioItems(
                                        id='analysis-type',
                                        options=[
                                            {"label": "Full Analysis", "value": "full"},
                                            {"label": "Quick Summary", "value": "summary"},
                                            {"label": "Scoring Only", "value": "scoring"},
                                            {"label": "Questions", "value": "questions"}
                                        ],
                                        value='full',
                                        inline=True,
                                        className="custom-radio",
                                        style={'color': '#B8BCC8'}
                                    )
                                ], md=6),
                                dbc.Col([
                                    html.Label("Enhanced Features", 
                                              style={'color': '#B8BCC8', 'fontSize': '14px', 'fontWeight': '500', 'marginBottom': '12px'}),
                                    dbc.Checklist(
                                        id='analysis-options',
                                        options=[
                                            {"label": "Web Search", "value": "web_search"},
                                            {"label": "AI Questions", "value": "questions"},
                                            {"label": "Deep Scoring", "value": "scoring"}
                                        ],
                                        value=['web_search', 'questions', 'scoring'],
                                        inline=True,
                                        style={'color': '#B8BCC8'}
                                    )
                                ], md=6)
                            ])
                        ]),
                        
                        # Analyze Button
                        html.Div([
                            dbc.Button(
                                [
                                    html.I(className="fas fa-rocket me-2"),
                                    html.Span("ANALYZE STARTUP", id="button-text")
                                ],
                                id='analyze-button',
                                color="primary",
                                size="lg",
                                className="w-100",
                                disabled=True,
                                style={'marginTop': '30px', 'padding': '16px'}
                            )
                        ]),
                        
                        # Progress indicator
                        html.Div(id='progress-container', className='mt-3')
                        
                    ], className='glass-card', style={'padding': '30px'})
                ])
            ], width=12)
        ], className='mb-4'),
        
        # Results Section
        dcc.Loading(
            id="loading-results",
            type="circle",
            children=[
                html.Div(id='analysis-results')
            ],
            color="#4C7BF4"
        )
        
    ], fluid=True),
    
    # Hidden stores
    dcc.Store(id='analysis-data'),
    dcc.Store(id='uploaded-files-store')
    
], className='main-container')

# Check system status
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
            
            status_badges = []
            if api_status.get('google_ai'):
                status_badges.append(
                    html.Span("AI Ready", 
                             className="badge badge-success me-2", 
                             style={'background': 'linear-gradient(135deg, #00D9A3 0%, #00B88C 100%)'})
                )
            
            if api_status.get('tavily_search'):
                status_badges.append(
                    html.Span("Web Search", 
                             className="badge badge-info me-2", 
                             style={'background': 'linear-gradient(135deg, #00B4D8 0%, #0096C7 100%)'})
                )
            
            return html.Div([
                html.Span("System Status: ", style={'color': '#6C7293', 'fontSize': '14px'}),
                html.Span("ONLINE", 
                         style={'color': '#00D9A3', 'fontWeight': '700', 'marginRight': '12px'}),
                *status_badges
            ])
    except:
        return html.Div([
            html.Span("System Status: ", style={'color': '#6C7293', 'fontSize': '14px'}),
            html.Span("OFFLINE", 
                     style={'color': '#FF5E5B', 'fontWeight': '700'})
        ])

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
        return html.Div(
            "No files uploaded", 
            style={'color': '#6C7293', 'textAlign': 'center', 'padding': '20px'}
        ), True, None
    
    files_info = []
    total_size = 0
    
    for content, filename in zip(contents, filenames):
        content_string = content.split(',')[1]
        decoded = base64.b64decode(content_string)
        file_size = len(decoded)
        total_size += file_size
        
        ext = os.path.splitext(filename)[1].lower()
        
        # File type colors
        ext_colors = {
            '.pdf': '#FF5E5B',
            '.xlsx': '#00D9A3',
            '.xls': '#00D9A3',
            '.csv': '#00D9A3',
            '.pptx': '#FFB547',
            '.txt': '#00B4D8',
            '.json': '#4C7BF4'
        }
        
        files_info.append({
            'filename': filename,
            'size': file_size,
            'color': ext_colors.get(ext, '#B8BCC8'),
            'content': content,
            'ext': ext
        })
    
    # Create file cards
    file_cards = []
    for info in files_info:
        size_str = f"{info['size']/1024:.1f} KB" if info['size'] < 1024*1024 else f"{info['size']/(1024*1024):.1f} MB"
        
        file_cards.append(
            html.Div([
                html.Div([
                    html.Div(info['ext'].upper()[1:], 
                            style={
                                'color': info['color'],
                                'fontSize': '12px',
                                'fontWeight': '700',
                                'marginBottom': '4px'
                            }),
                    html.Div(info['filename'], 
                            style={
                                'color': '#FFFFFF',
                                'fontSize': '14px',
                                'fontWeight': '500',
                                'marginBottom': '4px',
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'whiteSpace': 'nowrap'
                            }),
                    html.Div(size_str, 
                            style={'color': '#6C7293', 'fontSize': '12px'})
                ], style={
                    'padding': '12px',
                    'background': '#262B47',
                    'border': f'1px solid {info["color"]}33',
                    'borderRadius': '8px',
                    'marginBottom': '8px'
                })
            ])
        )
    
    files_display = html.Div([
        html.Div([
            html.Span(f"{len(files_info)} files ready • ", 
                     style={'color': '#B8BCC8', 'fontSize': '14px'}),
            html.Span(f"{total_size/(1024*1024):.1f} MB total", 
                     style={'color': '#6C7293', 'fontSize': '14px'})
        ], style={'marginBottom': '12px'}),
        html.Div(file_cards)
    ])
    
    return files_display, False, files_info

# Perform analysis
@app.callback(
    [Output('analysis-results', 'children'),
     Output('progress-container', 'children')],
    Input('analyze-button', 'n_clicks'),
    [State('uploaded-files-store', 'data'),
     State('analysis-type', 'value'),
     State('analysis-options', 'value')],
    prevent_initial_call=True
)
def perform_analysis(n_clicks, files_info, analysis_type, options):
    if not n_clicks or not files_info:
        raise PreventUpdate
    
    # Show progress
    progress = html.Div([
        dbc.Progress(value=100, animated=True, striped=True, 
                    style={'height': '6px', 'marginBottom': '8px'}),
        html.P("Processing with AI agents...", 
              style={'color': '#B8BCC8', 'fontSize': '14px', 'textAlign': 'center'})
    ])
    
    try:
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
        
        # Make request with extended timeout
        response = requests.post(f"{API_URL}{endpoint}", files=files_to_upload, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            results = create_professional_results(data, analysis_type)
            return results, None
        else:
            error = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Analysis failed: {response.text}"
            ], color="danger", style={'borderRadius': '12px'})
            return error, None
            
    except Exception as e:
        error = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {str(e)}"
        ], color="warning", style={'borderRadius': '12px'})
        return error, None

def create_professional_results(data, analysis_type):
    """Create professional results display with all sections."""
    
    components = []
    
    # Success notification
    if data.get('status') == 'success':
        processing_time = data.get('metadata', {}).get('processing_time_seconds', 0)
        components.append(
            dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Analysis completed successfully",
                html.Span(f" ({processing_time:.1f}s)" if processing_time else "", 
                         style={'color': '#6C7293', 'fontSize': '12px'})
            ], color="success", dismissable=True, style={'borderRadius': '12px'})
        )
    
    # Investment Score Overview
    if 'investment_scores' in data or 'overall_score' in data:
        components.append(create_score_overview(data))
    
    # Create comprehensive tabs
    tabs = []
    
    # Summary Tab
    if 'investment_summary' in data:
        tabs.append(dbc.Tab(
            create_summary_content(data),
            label="📝 Summary",
            tab_id="summary"
        ))
    
    # Scoring Tab
    if 'investment_scores' in data:
        tabs.append(dbc.Tab(
            create_detailed_scores(data),
            label="📊 Scoring",
            tab_id="scoring"
        ))
    
    # Questions Tab
    if 'founder_questions' in data or 'founder_interview_guide' in data:
        tabs.append(dbc.Tab(
            create_questions_content(data),
            label="❓ Questions",
            tab_id="questions"
        ))
    
    # Agent Analyses Tab
    if 'specialized_analyses' in data:
        tabs.append(dbc.Tab(
            create_agent_analyses_content(data),
            label="🤖 Agent Analysis",
            tab_id="agents"
        ))
    
    # Web Intelligence Tab
    if 'web_intelligence' in data:
        tabs.append(dbc.Tab(
            create_web_intelligence_content(data),
            label="🌐 Web Intel",
            tab_id="web"
        ))
    
    # Processing Details Tab
    if 'processing_summary' in data or 'metadata' in data:
        tabs.append(dbc.Tab(
            create_processing_details(data),
            label="ℹ️ Details",
            tab_id="details"
        ))
    
    if tabs:
        components.append(
            html.Div([
                dbc.Tabs(tabs, active_tab=tabs[0].tab_id if tabs else None)
            ], className='glass-card', style={'padding': '20px', 'marginTop': '20px'})
        )
    
    # Download button
    components.append(
        html.Div([
            dbc.Button([
                html.I(className="fas fa-download me-2"),
                "EXPORT REPORT"
            ], color="secondary", size="lg", className="mt-4",
               style={'padding': '12px 32px', 'fontWeight': '600'})
        ], style={'textAlign': 'center', 'marginTop': '30px'})
    )
    
    return html.Div(components)

def create_agent_analyses_content(data):
    """Create specialized agent analyses display with full content."""
    
    analyses = data.get('specialized_analyses', {})
    
    if not analyses:
        return html.Div([
            html.P("No specialized analyses available", 
                  style={'color': '#6C7293', 'textAlign': 'center', 'padding': '40px'})
        ])
    
    agent_cards = []
    
    agent_info = {
        'pitch_deck': ('📊', '#4C7BF4', 'Pitch Deck Analysis'),
        'data_room': ('💰', '#00D9A3', 'Financial & Traction'),
        'web_content': ('🌐', '#00B4D8', 'Web Intelligence'),
        'interaction': ('💬', '#FFB547', 'Interaction Signals')
    }
    
    for agent, content in analyses.items():
        icon, color, title = agent_info.get(agent, ('🤖', '#B8BCC8', agent.replace('_', ' ').title()))
        confidence = content.get('confidence', 0)
        analysis_text = content.get('analysis', '')
        
        # Don't truncate web content analysis - show it all
        if agent == 'web_content':
            # Web content gets special treatment - full display
            agent_cards.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(icon, style={'fontSize': '24px', 'marginRight': '12px'}),
                            html.Span(title, 
                                     style={'color': '#FFFFFF', 'fontSize': '18px', 'fontWeight': '600'}),
                            html.Span(f"{confidence:.0%}", 
                                     style={'color': color, 'fontSize': '14px', 'float': 'right', 
                                           'fontWeight': '600'})
                        ], style={'marginBottom': '16px'}),
                        
                        # Full content for web intelligence
                        html.Div([
                            dcc.Markdown(
                                analysis_text,  # Full text, no truncation
                                style={'color': '#B8BCC8', 'fontSize': '14px', 'lineHeight': '1.8'},
                                className='markdown-content'
                            )
                        ], style={
                            'maxHeight': '600px',  # Increased height for web content
                            'overflowY': 'auto',
                            'paddingRight': '10px'
                        })
                    ], style={
                        'padding': '20px',
                        'background': '#262B47',
                        'borderLeft': f'4px solid {color}',
                        'borderRadius': '8px',
                        'marginBottom': '16px'
                    })
                ])
            )
        else:
            # Other agents get truncated display
            agent_cards.append(
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span(icon, style={'fontSize': '24px', 'marginRight': '12px'}),
                            html.Span(title, 
                                     style={'color': '#FFFFFF', 'fontSize': '18px', 'fontWeight': '600'}),
                            html.Span(f"{confidence:.0%}", 
                                     style={'color': color, 'fontSize': '14px', 'float': 'right', 
                                           'fontWeight': '600'})
                        ], style={'marginBottom': '16px'}),
                        
                        html.Div([
                            dcc.Markdown(
                                analysis_text[:2000] + "..." if len(analysis_text) > 2000 else analysis_text,
                                style={'color': '#B8BCC8', 'fontSize': '14px', 'lineHeight': '1.6'},
                                className='markdown-content'
                            )
                        ], style={
                            'maxHeight': '400px',
                            'overflowY': 'auto',
                            'paddingRight': '10px'
                        })
                    ], style={
                        'padding': '20px',
                        'background': '#262B47',
                        'borderLeft': f'4px solid {color}',
                        'borderRadius': '8px',
                        'marginBottom': '16px'
                    })
                ])
            )
    
    return html.Div([
        html.H4("Specialized Agent Analyses", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        html.Div(agent_cards)
    ], style={'padding': '20px'})

def create_web_intelligence_content(data):
    """Create comprehensive web intelligence display."""
    
    web_intel = data.get('web_intelligence', {})
    company_info = web_intel.get('company_info', {})
    search_performed = web_intel.get('search_performed', False)
    
    components = []
    
    # Company Information Card with better formatting
    if company_info and any(company_info.values()):
        info_rows = []
        
        # Main company info
        if company_info.get('name'):
            info_rows.append(
                html.Tr([
                    html.Td("Company", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px'}),
                    html.Td(company_info['name'], style={'color': '#FFFFFF', 'fontWeight': '600', 'padding': '8px'})
                ])
            )
        
        if company_info.get('industry'):
            info_rows.append(
                html.Tr([
                    html.Td("Industry", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px'}),
                    html.Td(company_info['industry'], style={'color': '#FFFFFF', 'padding': '8px'})
                ])
            )
        
        if company_info.get('website'):
            info_rows.append(
                html.Tr([
                    html.Td("Website", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px'}),
                    html.Td(company_info['website'], style={'color': '#00B4D8', 'padding': '8px'})
                ])
            )
        
        if company_info.get('location'):
            info_rows.append(
                html.Tr([
                    html.Td("Location", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px'}),
                    html.Td(company_info['location'], style={'color': '#FFFFFF', 'padding': '8px'})
                ])
            )
        
        if company_info.get('stage'):
            info_rows.append(
                html.Tr([
                    html.Td("Stage", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px'}),
                    html.Td(company_info['stage'], style={'color': '#FFFFFF', 'padding': '8px'})
                ])
            )
        
        if company_info.get('description'):
            info_rows.append(
                html.Tr([
                    html.Td("Description", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px', 'verticalAlign': 'top'}),
                    html.Td(company_info['description'], style={'color': '#B8BCC8', 'padding': '8px'})
                ])
            )
        
        # Products/Services
        if company_info.get('products') and len(company_info['products']) > 0:
            products_list = html.Ul([
                html.Li(product, style={'color': '#B8BCC8', 'marginBottom': '4px'}) 
                for product in company_info['products']
            ])
            info_rows.append(
                html.Tr([
                    html.Td("Products", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px', 'verticalAlign': 'top'}),
                    html.Td(products_list, style={'padding': '8px'})
                ])
            )
        
        # Founders
        if company_info.get('founders') and len(company_info['founders']) > 0:
            founders_list = html.Ul([
                html.Li(founder, style={'color': '#B8BCC8', 'marginBottom': '4px'}) 
                for founder in company_info['founders']
            ])
            info_rows.append(
                html.Tr([
                    html.Td("Founders", style={'color': '#6C7293', 'fontWeight': '500', 'padding': '8px', 'verticalAlign': 'top'}),
                    html.Td(founders_list, style={'padding': '8px'})
                ])
            )
        
        components.append(
            html.Div([
                html.H5("Company Intelligence", 
                       style={'color': '#4C7BF4', 'marginBottom': '16px', 'fontWeight': '600'}),
                html.Table([
                    html.Tbody(info_rows)
                ], style={
                    'width': '100%',
                    'background': '#262B47',
                    'borderRadius': '8px',
                    'overflow': 'hidden'
                })
            ], style={'marginBottom': '30px'})
        )
    
    # Web Search Results from specialized analyses
    specialized_analyses = data.get('specialized_analyses', {})
    if 'web_content' in specialized_analyses:
        web_analysis = specialized_analyses['web_content'].get('analysis', '')
        
        # Extract web search results section
        if '**WEB SEARCH RESULTS:**' in web_analysis or 'search results' in web_analysis.lower():
            components.append(
                html.Div([
                    html.H5("Web Search Analysis", 
                           style={'color': '#4C7BF4', 'marginBottom': '16px', 'fontWeight': '600'}),
                    html.Div([
                        dcc.Markdown(
                            web_analysis,
                            style={'color': '#B8BCC8', 'fontSize': '14px', 'lineHeight': '1.8'},
                            className='markdown-content'
                        )
                    ], style={
                        'background': '#262B47',
                        'padding': '20px',
                        'borderRadius': '8px',
                        'maxHeight': '800px',
                        'overflowY': 'auto'
                    })
                ])
            )
    
    # Search Status
    if search_performed:
        components.insert(0,
            html.Div([
                html.I(className="fas fa-check-circle me-2", style={'color': '#00D9A3'}),
                html.Span("Web search completed successfully", style={'color': '#00D9A3', 'fontWeight': '500'}),
                html.P("Competitive intelligence and market validation data has been integrated into the analysis.",
                      style={'color': '#B8BCC8', 'fontSize': '14px', 'marginTop': '8px'})
            ], style={
                'padding': '16px',
                'background': 'rgba(0, 217, 163, 0.1)',
                'border': '1px solid rgba(0, 217, 163, 0.3)',
                'borderRadius': '8px',
                'marginBottom': '20px'
            })
        )
    else:
        components.insert(0,
            html.Div([
                html.I(className="fas fa-info-circle me-2", style={'color': '#FFB547'}),
                html.Span("Web search not performed", style={'color': '#FFB547', 'fontWeight': '500'}),
                html.P("Web search was not executed. Check Tavily API configuration.",
                      style={'color': '#B8BCC8', 'fontSize': '14px', 'marginTop': '8px'})
            ], style={
                'padding': '16px',
                'background': 'rgba(255, 181, 71, 0.1)',
                'border': '1px solid rgba(255, 181, 71, 0.3)',
                'borderRadius': '8px',
                'marginBottom': '20px'
            })
        )
    
    return html.Div([
        html.H4("Web Intelligence & Search Results", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        html.Div(components if components else 
                [html.P("No web intelligence data available", style={'color': '#6C7293', 'textAlign': 'center'})])
    ], style={'padding': '20px'})

def create_processing_details(data):
    """Create processing details and metadata display."""
    
    processing = data.get('processing_summary', {})
    metadata = data.get('metadata', {})
    
    details = []
    
    # Files processed
    if processing.get('categories'):
        for category, info in processing['categories'].items():
            details.append(
                html.Div([
                    html.Span(category.replace('_', ' ').title(), 
                             style={'color': '#4C7BF4', 'fontWeight': '600'}),
                    html.Span(f": {info['file_count']} files", 
                             style={'color': '#B8BCC8', 'marginLeft': '8px'})
                ], style={'marginBottom': '8px'})
            )
    
    # Processing metrics
    metrics = []
    if metadata.get('total_files_processed'):
        metrics.append(
            html.Div([
                html.Div(str(metadata['total_files_processed']), 
                        style={'fontSize': '24px', 'fontWeight': '700', 'color': '#4C7BF4'}),
                html.Div("Files", style={'color': '#6C7293', 'fontSize': '12px'})
            ], style={'textAlign': 'center'})
        )
    
    if metadata.get('processing_time_seconds'):
        metrics.append(
            html.Div([
                html.Div(f"{metadata['processing_time_seconds']:.1f}s", 
                        style={'fontSize': '24px', 'fontWeight': '700', 'color': '#00D9A3'}),
                html.Div("Time", style={'color': '#6C7293', 'fontSize': '12px'})
            ], style={'textAlign': 'center'})
        )
    
    if metadata.get('agents_used'):
        metrics.append(
            html.Div([
                html.Div(str(metadata['agents_used']), 
                        style={'fontSize': '24px', 'fontWeight': '700', 'color': '#FFB547'}),
                html.Div("Agents", style={'color': '#6C7293', 'fontSize': '12px'})
            ], style={'textAlign': 'center'})
        )
    
    return html.Div([
        html.H4("Processing Details", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        dbc.Row([dbc.Col(m, md=4) for m in metrics]) if metrics else None,
        html.Hr(style={'borderColor': '#2D3254', 'margin': '20px 0'}),
        html.Div(details)
    ], style={'padding': '20px'})

def create_score_overview(data):
    """Create investment score overview."""
    
    scores = data.get('investment_scores', {})
    overall = scores.get('overall_weighted', 0)
    recommendation = scores.get('recommendation', 'Hold')
    
    # Determine color based on score
    if overall >= 75:
        score_color = '#00D9A3'
        rec_class = 'score-excellent'
    elif overall >= 60:
        score_color = '#00B4D8'
        rec_class = 'score-good'
    elif overall >= 45:
        score_color = '#FFB547'
        rec_class = 'score-moderate'
    else:
        score_color = '#FF5E5B'
        rec_class = 'score-poor'
    
    # Create metrics cards
    metrics = []
    for key, label in [
        ('team', 'Team'),
        ('market', 'Market'),
        ('product', 'Product'),
        ('traction', 'Traction'),
        ('financials', 'Financials'),
        ('moat', 'Moat')
    ]:
        value = scores.get(key, 0)
        metrics.append(
            dbc.Col([
                html.Div([
                    html.Div(f"{value:.0f}", className='metric-value'),
                    html.Div(label.upper(), className='metric-label')
                ], className='metric-card')
            ], md=2)
        )
    
    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1(f"{overall:.0f}", 
                               style={
                                   'fontSize': '72px',
                                   'fontWeight': '700',
                                   'color': score_color,
                                   'marginBottom': '8px'
                               }),
                        html.P("OVERALL SCORE", 
                              style={'color': '#6C7293', 'fontSize': '14px', 'letterSpacing': '2px'}),
                        html.Div([
                            html.Span(recommendation.upper(), className=f'score-badge {rec_class}')
                        ], style={'marginTop': '16px'})
                    ], style={'textAlign': 'center'})
                ], md=4),
                dbc.Col([
                    dbc.Row(metrics)
                ], md=8)
            ])
        ], className='glass-card', style={'padding': '30px'})
    ], style={'marginBottom': '20px'})

def create_summary_content(data):
    """Create executive summary content with proper markdown rendering."""
    
    summary = data.get('investment_summary', '')
    confidence = data.get('confidence_score', 0)
    
    # Create confidence indicator
    confidence_color = '#00D9A3' if confidence > 0.7 else '#FFB547' if confidence > 0.5 else '#FF5E5B'
    
    return html.Div([
        # Confidence Score Header
        html.Div([
            html.Div([
                html.Span("Analysis Confidence: ", style={'color': '#B8BCC8', 'fontSize': '14px'}),
                html.Span(f"{confidence:.1%}", 
                         style={'color': confidence_color, 'fontSize': '18px', 'fontWeight': '700'})
            ], style={'textAlign': 'right', 'marginBottom': '20px'})
        ]),
        
        # Executive Summary with Markdown rendering
        html.Div([
            html.H4("Executive Summary", 
                   style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
            
            # Use Markdown component for proper formatting
            dcc.Markdown(
                summary,
                style={
                    'color': '#B8BCC8',
                    'lineHeight': '1.8',
                    'fontSize': '15px'
                },
                # Custom CSS for markdown elements
                dangerously_allow_html=True,
                className='markdown-content'
            )
        ], style={'padding': '20px'})
    ])

def create_detailed_scores(data):
    """Create detailed scoring breakdown."""
    
    scores = data.get('investment_scores', {})
    weights = scores.get('weights', {})
    
    # Create radar chart
    categories = ['Team', 'Market', 'Product', 'Traction', 'Financials', 'Moat']
    values = [
        scores.get('team', 0),
        scores.get('market', 0),
        scores.get('product', 0),
        scores.get('traction', 0),
        scores.get('financials', 0),
        scores.get('moat', 0)
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#4C7BF4',
        fillcolor='rgba(76, 123, 244, 0.3)',
        marker=dict(color='#4C7BF4', size=8)
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor='#1A1F3A',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='#2D3254',
                linecolor='#2D3254',
                tickfont=dict(color='#6C7293', size=10)
            ),
            angularaxis=dict(
                gridcolor='#2D3254',
                linecolor='#2D3254',
                tickfont=dict(color='#B8BCC8', size=12)
            )
        ),
        showlegend=False,
        paper_bgcolor='#1A1F3A',
        plot_bgcolor='#1A1F3A',
        height=400,
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(color='#B8BCC8')
    )
    
    # Create score table
    table_data = []
    for key, label in [
        ('team', 'Team'),
        ('market', 'Market'),
        ('product', 'Product'),
        ('traction', 'Traction'),
        ('financials', 'Financials'),
        ('moat', 'Moat')
    ]:
        score_val = scores.get(key, 0)
        weight_val = weights.get(key, 0) if weights else 0
        weighted = score_val * weight_val
        
        table_data.append({
            'Category': label,
            'Score': f"{score_val:.0f}",
            'Weight': f"{weight_val*100:.0f}%",
            'Contribution': f"{weighted:.1f}"
        })
    
    return html.Div([
        html.H4("Scoring Analysis", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ], md=6),
            dbc.Col([
                dash_table.DataTable(
                    data=table_data,
                    columns=[{"name": i, "id": i} for i in ['Category', 'Score', 'Weight', 'Contribution']],
                    style_cell={
                        'textAlign': 'center',
                        'backgroundColor': '#1A1F3A',
                        'color': '#B8BCC8',
                        'border': '1px solid #2D3254'
                    },
                    style_header={
                        'backgroundColor': '#262B47',
                        'color': '#FFFFFF',
                        'fontWeight': '600',
                        'border': '1px solid #2D3254'
                    },
                    style_data_conditional=[
                        {
                            'if': {'column_id': 'Score'},
                            'color': '#4C7BF4',
                            'fontWeight': '600'
                        }
                    ]
                )
            ], md=6)
        ])
    ], style={'padding': '20px'})

def create_questions_content(data):
    """Create founder questions content with proper formatting."""
    
    questions_text = data.get('founder_questions', '') or data.get('founder_interview_guide', '')
    top_questions = data.get('top_founder_questions', [])
    gaps = data.get('identified_gaps', '')
    
    components = []
    
    # Add gaps section if available
    if gaps:
        components.append(
            html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2", style={'color': '#FFB547'}),
                    html.Span("Information Gaps Identified", 
                             style={'color': '#FFB547', 'fontWeight': '600', 'fontSize': '16px'})
                ], style={'marginBottom': '12px'}),
                dcc.Markdown(
                    gaps,
                    style={'color': '#B8BCC8', 'fontSize': '14px', 'lineHeight': '1.6'},
                    className='markdown-content'
                )
            ], style={
                'padding': '20px',
                'background': 'rgba(255, 181, 71, 0.1)',
                'border': '1px solid rgba(255, 181, 71, 0.3)',
                'borderRadius': '8px',
                'marginBottom': '20px'
            })
        )
    
    # Priority questions section
    if top_questions:
        priority_questions = []
        for i, q in enumerate(top_questions[:10], 1):
            priority_questions.append(
                html.Div([
                    html.Div([
                        html.Span(f"{i:02d}", 
                                 style={
                                     'color': '#4C7BF4',
                                     'fontSize': '18px',
                                     'fontWeight': '700',
                                     'marginRight': '16px',
                                     'minWidth': '35px'
                                 }),
                        html.Span(q, style={'color': '#FFFFFF', 'fontSize': '15px', 'flex': '1'})
                    ], style={
                        'padding': '16px',
                        'background': '#262B47',
                        'borderLeft': '3px solid #4C7BF4',
                        'borderRadius': '8px',
                        'marginBottom': '12px',
                        'display': 'flex',
                        'alignItems': 'flex-start'
                    })
                ])
            )
        
        components.append(
            html.Div([
                html.H5("Priority Questions for Founders", 
                       style={'color': '#4C7BF4', 'marginBottom': '16px', 'fontWeight': '600'}),
                html.Div(priority_questions)
            ])
        )
    
    # Full questions with markdown rendering
    if questions_text and not top_questions:
        components.append(
            html.Div([
                html.H5("Founder Interview Guide", 
                       style={'color': '#4C7BF4', 'marginBottom': '16px', 'fontWeight': '600'}),
                dcc.Markdown(
                    questions_text,
                    style={
                        'color': '#B8BCC8',
                        'lineHeight': '1.8',
                        'fontSize': '15px'
                    },
                    className='markdown-content'
                )
            ])
        )
    
    return html.Div([
        html.H4("Due Diligence Questions", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        html.Div(components if components else 
                [html.P("No questions generated", style={'color': '#6C7293'})])
    ], style={'padding': '20px'})

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)