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

app.title = "VentureIQ - AI Investment Analysis"

# Backend API URL
API_URL = os.getenv("API_URL", "http://0.0.0.0:8443")

# Modern Professional Color Palette (Claude/ChatGPT inspired)
COLORS = {
    'background': '#0F1419',        # Very dark slate
    'sidebar_bg': '#1A1D24',        # Sidebar background
    'surface': '#212530',           # Card/surface background
    'surface_hover': '#2A2F3C',     # Hover state
    'border': '#2E3340',            # Subtle borders
    'primary': '#6366F1',           # Modern indigo
    'primary_hover': '#4F46E5',     # Darker indigo
    'success': '#10B981',           # Modern green
    'warning': '#F59E0B',           # Modern amber
    'danger': '#EF4444',            # Modern red
    'info': '#3B82F6',              # Modern blue
    'text_primary': '#F3F4F6',      # Almost white
    'text_secondary': '#9CA3AF',    # Medium gray
    'text_muted': '#6B7280',        # Muted gray
    'accent': '#8B5CF6',            # Purple accent
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
                background: #0F1419;
                color: #F3F4F6;
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                margin: 0;
                padding: 0;
                overflow: hidden;
            }

            /* Layout Container */
            .app-container {
                display: flex;
                height: 100vh;
                width: 100vw;
                overflow: hidden;
            }

            /* Left Sidebar */
            .sidebar {
                width: 380px;
                background: #1A1D24;
                border-right: 1px solid #2E3340;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }

            .sidebar-header {
                padding: 20px 24px;
                border-bottom: 1px solid #2E3340;
                background: linear-gradient(180deg, #1A1D24 0%, #171A1F 100%);
            }

            .sidebar-content {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }

            .sidebar-content::-webkit-scrollbar {
                width: 6px;
            }

            .sidebar-content::-webkit-scrollbar-track {
                background: transparent;
            }

            .sidebar-content::-webkit-scrollbar-thumb {
                background: #2E3340;
                border-radius: 3px;
            }

            .sidebar-content::-webkit-scrollbar-thumb:hover {
                background: #3E4350;
            }

            .sidebar-footer {
                padding: 16px 24px;
                border-top: 1px solid #2E3340;
                text-align: center;
                color: #6B7280;
                font-size: 12px;
                flex-shrink: 0;
                background: #1A1D24;
            }

            /* Main Content Area */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                background: #0F1419;
            }

            .content-header {
                padding: 20px 32px;
                border-bottom: 1px solid #2E3340;
                background: #1A1D24;
            }

            .content-body {
                flex: 1;
                overflow-y: auto;
                padding: 32px;
            }

            .content-body::-webkit-scrollbar {
                width: 8px;
            }

            .content-body::-webkit-scrollbar-track {
                background: transparent;
            }

            .content-body::-webkit-scrollbar-thumb {
                background: #2E3340;
                border-radius: 4px;
            }

            .content-body::-webkit-scrollbar-thumb:hover {
                background: #3E4350;
            }

            /* Cards & Panels */
            .glass-panel {
                background: #212530;
                border: 1px solid #2E3340;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                transition: all 0.2s ease;
                overflow: hidden;
                box-sizing: border-box;
            }

            .glass-panel:hover {
                border-color: #3E4350;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            }

            .glass-panel * {
                max-width: 100%;
                box-sizing: border-box;
            }

            .analysis-card {
                background: #212530;
                border: 1px solid #2E3340;
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .analysis-card:hover {
                background: #2A2F3C;
                border-color: #6366F1;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
            }

            /* Upload Area */
            .upload-area {
                background: #212530;
                border: 2px dashed #2E3340;
                border-radius: 12px;
                padding: 40px 20px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .upload-area:hover {
                border-color: #6366F1;
                background: #2A2F3C;
            }

            /* Buttons */
            .btn-primary {
                background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
                border: none;
                color: white;
                font-weight: 500;
                transition: all 0.2s ease;
            }

            .btn-primary:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            }

            /* Badge Styles */
            .recommendation-badge {
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                display: inline-block;
            }

            .badge-strong-buy {
                background: rgba(16, 185, 129, 0.15);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }

            .badge-buy {
                background: rgba(59, 130, 246, 0.15);
                color: #3B82F6;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }

            .badge-hold {
                background: rgba(245, 158, 11, 0.15);
                color: #F59E0B;
                border: 1px solid rgba(245, 158, 11, 0.3);
            }

            .badge-pass {
                background: rgba(239, 68, 68, 0.15);
                color: #EF4444;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }

            /* Typography */
            h1, h2, h3, h4, h5, h6 {
                color: #F3F4F6;
                font-weight: 600;
            }

            .text-muted {
                color: #6B7280 !important;
            }

            .text-secondary {
                color: #9CA3AF !important;
            }

            /* Empty State */
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #6B7280;
            }

            .empty-state-icon {
                font-size: 48px;
                color: #3E4350;
                margin-bottom: 16px;
            }

            /* Section Divider */
            .section-divider {
                border-top: 1px solid #2E3340;
                margin: 24px 0;
            }

            /* Text Overflow Fixes */
            .analysis-card {
                overflow: hidden;
                width: 100%;
                box-sizing: border-box;
            }

            .sidebar-content {
                overflow-x: hidden;
                overflow-y: auto;
            }

            /* Prevent horizontal overflow in sidebar */
            .sidebar * {
                max-width: 100%;
                box-sizing: border-box;
            }

            /* Company name can wrap */
            .company-name {
                word-break: break-word;
                white-space: normal !important;
                overflow-wrap: break-word;
                overflow: visible !important;
                text-overflow: unset !important;
                line-height: 1.3;
            }

            /* Other text in cards should truncate */
            .analysis-card .text-truncate {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            /* Responsive sidebar */
            @media (max-width: 1400px) {
                .sidebar {
                    width: 340px;
                }
            }

            @media (max-width: 1200px) {
                .sidebar {
                    width: 300px;
                }
            }
            
            .glass-card {
                background: rgba(26, 31, 58, 0.8);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                transition: all 0.3s ease;
                overflow: hidden;
                box-sizing: border-box;
            }

            .glass-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 40px rgba(76, 123, 244, 0.3);
                border-color: rgba(76, 123, 244, 0.3);
            }

            .glass-card * {
                max-width: 100%;
                box-sizing: border-box;
            }
            
            .card {
                background: #1A1F3A;
                border: 1px solid #2D3254;
                border-radius: 12px;
                color: #FFFFFF;
                overflow: hidden;
                box-sizing: border-box;
            }

            .card * {
                max-width: 100%;
                box-sizing: border-box;
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
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                max-width: 100%;
                box-sizing: border-box;
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
                padding: 20px 16px;
                text-align: center;
                transition: all 0.3s ease;
                overflow: hidden;
                box-sizing: border-box;
                min-height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }

            .metric-card:hover {
                transform: translateY(-4px);
                border-color: #4C7BF4;
                box-shadow: 0 8px 24px rgba(76, 123, 244, 0.2);
            }

            .metric-value {
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(135deg, #4C7BF4 0%, #00D9A3 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 6px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                width: 100%;
            }

            .metric-label {
                color: #6C7293;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                width: 100%;
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

# App Layout - Modern Split View
app.layout = html.Div([
    # URL component for page load detection
    dcc.Location(id='url', refresh=False),

    # Hidden stores
    dcc.Store(id='uploaded-files-store', data=[]),
    dcc.Store(id='progress-store', data=0),
    dcc.Store(id='analysis-result-store', data={}),

    # Main App Container
    html.Div([
        # LEFT SIDEBAR
        html.Div([
            # Sidebar Header
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-brain",
                              style={'fontSize': '28px', 'color': COLORS['primary']}),
                    ], style={
                        'width': '48px',
                        'height': '48px',
                        'background': f"linear-gradient(135deg, {COLORS['primary']}20 0%, {COLORS['accent']}20 100%)",
                        'borderRadius': '12px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'marginRight': '12px',
                        'border': f"1px solid {COLORS['primary']}40"
                    }),
                    html.Div([
                        html.H4("VentureIQ",
                               style={'color': COLORS['text_primary'], 'fontWeight': '700', 'marginBottom': '2px', 'fontSize': '20px'}),
                        html.P("AI-Powered Investment Analysis",
                               style={'color': COLORS['text_muted'], 'marginBottom': '0', 'fontSize': '11px'})
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], className='sidebar-header'),

            # Sidebar Content
            html.Div([
                # Upload Section
                html.Div([
                    html.H5("New Analysis",
                           style={'color': COLORS['text_primary'], 'marginBottom': '16px', 'fontSize': '14px', 'fontWeight': '600'}),

                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            html.I(className="fas fa-cloud-upload-alt",
                                  style={'fontSize': '32px', 'color': COLORS['primary'], 'marginBottom': '12px'}),
                            html.P('Drop files or click',
                                  style={'color': COLORS['text_secondary'], 'marginBottom': '6px', 'fontSize': '13px'}),
                            html.P('PDF • XLSX • PPTX • CSV',
                                  style={'color': COLORS['text_muted'], 'marginBottom': '0', 'fontSize': '11px'})
                        ], className='upload-area', style={'textAlign': 'center'}),
                        multiple=True
                    ),

                    html.Div(id='uploaded-files', style={'marginTop': '12px'}),

                    # Analyze Button
                    html.Div([
                        dbc.Button(
                            [html.I(className="fas fa-robot me-2"), "Start Analysis"],
                            id='analyze-button',
                            color="primary",
                            size="md",
                            style={'width': '100%', 'marginTop': '16px', 'fontWeight': '600'},
                            disabled=True
                        )
                    ]),

                ], style={'marginBottom': '32px'}),

                # Divider
                html.Hr(className='section-divider'),

                # Saved Analyses Section
                html.Div([
                    html.Div([
                        html.H5("Previous Analyses",
                               style={'color': COLORS['text_primary'], 'fontSize': '14px', 'fontWeight': '600', 'marginBottom': '4px'}),
                        html.P("Click to view saved results",
                              style={'color': COLORS['text_muted'], 'fontSize': '12px', 'marginBottom': '16px'}),
                    ]),

                    # Refresh button
                    dbc.Button(
                        [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                        id='refresh-analyses-btn',
                        color="secondary",
                        size="sm",
                        outline=True,
                        style={'marginBottom': '16px', 'fontSize': '12px'}
                    ),

                    # Saved analyses list
                    html.Div(id='saved-analyses-list'),

                ])

            ], className='sidebar-content'),

            # Sidebar Footer
            html.Div([
                html.P(["© 2025 ", html.B("Foresvest"), ". All rights reserved."],
                       style={'margin': '0', 'color': COLORS['text_muted'], 'fontSize': '12px'})
            ], className='sidebar-footer'),

        ], className='sidebar'),

        # RIGHT MAIN CONTENT
        html.Div([
            # Content Header
            html.Div([
                html.Div([
                    html.H3("Analysis Results",
                           style={'color': COLORS['text_primary'], 'marginBottom': '4px', 'fontSize': '20px', 'fontWeight': '600'}),
                    html.P("Investment evaluation powered by multi-agent AI",
                           style={'color': COLORS['text_muted'], 'marginBottom': '0', 'fontSize': '13px'}),
                ]),
                html.Div(id='system-status')
            ], className='content-header', style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),

            # Content Body
            html.Div([
                # Progress container
                html.Div(id='progress-container'),

                # Analysis Results
                html.Div(id='analysis-results', children=[
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-lightbulb empty-state-icon"),
                        ], style={'marginBottom': '16px'}),
                        html.H4("Ready to Analyze",
                               style={'color': COLORS['text_secondary'], 'marginBottom': '8px', 'fontSize': '18px'}),
                        html.P("Upload documents in the sidebar to start your investment analysis",
                               style={'color': COLORS['text_muted'], 'fontSize': '14px', 'maxWidth': '400px', 'margin': '0 auto'})
                    ], className='empty-state')
                ]),

            ], className='content-body')
        ], className='main-content')

    ], className='app-container')

], style={'width': '100vw', 'height': '100vh', 'overflow': 'hidden'})

# Check system status
@app.callback(
    Output('system-status', 'children'),
    Input('system-status', 'id')
)
def check_system_status(_):
    try:
        response = requests.get(f"{API_URL}/health", timeout=15)
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

# Callback to immediately disable button and show loading state when clicked
@app.callback(
    [Output('analyze-button', 'disabled'),
     Output('analyze-button', 'children')],
    Input('analyze-button', 'n_clicks'),
    State('analyze-button', 'disabled'),
    prevent_initial_call=True
)
def disable_button_on_click(n_clicks, current_disabled):
    """Immediately disable button and show loading state when clicked."""
    if n_clicks and not current_disabled:
        # Show loading state
        loading_content = [
            html.I(className="fas fa-spinner fa-spin me-2"),
            "Analyzing..."
        ]
        return True, loading_content
    raise PreventUpdate

# Handle file uploads with better multiple file support
@app.callback(
    [Output('uploaded-files', 'children'),
     Output('analyze-button', 'disabled', allow_duplicate=True),
     Output('uploaded-files-store', 'data')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def handle_file_upload(contents, filenames):
    if not contents:
        empty_state = html.Div([
            html.I(className="fas fa-folder-open", 
                  style={'fontSize': '32px', 'color': '#6C7293', 'marginBottom': '12px'}),
            html.P("No files uploaded yet", 
                  style={'color': '#6C7293', 'fontSize': '14px'}),
            html.P("Select multiple files using Ctrl/Cmd+Click or drag multiple files", 
                  style={'color': '#6C7293', 'fontSize': '12px'})
        ], style={'textAlign': 'center', 'padding': '30px'})
        
        return empty_state, True, None
    
    # Handle both single and multiple files
    if not isinstance(contents, list):
        contents = [contents]
        filenames = [filenames]
    
    files_info = []
    total_size = 0
    
    for content, filename in zip(contents, filenames):
        try:
            content_string = content.split(',')[1]
            decoded = base64.b64decode(content_string)
            file_size = len(decoded)
            total_size += file_size
            
            ext = os.path.splitext(filename)[1].lower()
            
            # File type colors and icons
            file_types = {
                '.pdf': {'color': '#FF5E5B', 'icon': 'fa-file-pdf'},
                '.xlsx': {'color': '#00D9A3', 'icon': 'fa-file-excel'},
                '.xls': {'color': '#00D9A3', 'icon': 'fa-file-excel'},
                '.csv': {'color': '#00D9A3', 'icon': 'fa-file-csv'},
                '.pptx': {'color': '#FFB547', 'icon': 'fa-file-powerpoint'},
                '.ppt': {'color': '#FFB547', 'icon': 'fa-file-powerpoint'},
                '.txt': {'color': '#00B4D8', 'icon': 'fa-file-alt'},
                '.md': {'color': '#00B4D8', 'icon': 'fa-file-alt'},
                '.json': {'color': '#4C7BF4', 'icon': 'fa-file-code'}
            }
            
            file_info = file_types.get(ext, {'color': '#B8BCC8', 'icon': 'fa-file'})
            
            files_info.append({
                'filename': filename,
                'size': file_size,
                'color': file_info['color'],
                'icon': file_info['icon'],
                'content': content,
                'ext': ext
            })
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            continue
    
    # Create file cards grid
    file_cards = []
    for i, info in enumerate(files_info):
        size_str = f"{info['size']/1024:.1f} KB" if info['size'] < 1024*1024 else f"{info['size']/(1024*1024):.1f} MB"
        
        file_cards.append(
            dbc.Col([
                html.Div([
                    html.Div([
                        html.I(className=f"fas {info['icon']}", 
                              style={'fontSize': '24px', 'color': info['color'], 'marginBottom': '8px'}),
                        html.Div(info['filename'], 
                                style={
                                    'color': '#FFFFFF',
                                    'fontSize': '13px',
                                    'fontWeight': '500',
                                    'marginBottom': '4px',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'whiteSpace': 'nowrap'
                                },
                                title=info['filename']),  # Tooltip for full name
                        html.Div(size_str, 
                                style={'color': '#6C7293', 'fontSize': '11px'})
                    ], style={
                        'padding': '15px',
                        'background': '#262B47',
                        'border': f'1px solid {info["color"]}33',
                        'borderRadius': '8px',
                        'textAlign': 'center',
                        'height': '120px',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                        'transition': 'all 0.3s ease',
                        'cursor': 'pointer'
                    },
                    className='file-card-hover')
                ])
            ], width=6, md=4, lg=3, className='mb-3')
        )
    
    # File count banner (integrated into the display)
    file_count_banner = html.Div([
        html.I(className="fas fa-check-circle me-2", style={'color': '#00D9A3'}),
        html.Span(f"{len(files_info)} file{'s' if len(files_info) > 1 else ''} ready for analysis", 
                 style={'color': '#00D9A3', 'fontWeight': '600'}),
        html.Span(f" • Total size: {total_size/(1024*1024):.1f} MB", 
                 style={'color': '#B8BCC8', 'fontSize': '14px'})
    ], style={
        'padding': '12px',
        'background': 'rgba(0, 217, 163, 0.1)',
        'border': '1px solid rgba(0, 217, 163, 0.3)',
        'borderRadius': '8px',
        'marginBottom': '16px'
    })
    
    files_display = html.Div([
        file_count_banner,
        dbc.Row(file_cards)
    ])
    
    return files_display, False, files_info

# Perform analysis
@app.callback(
    [Output('analysis-results', 'children'),
     Output('progress-container', 'children'),
     Output('analysis-result-store', 'data'),
     Output('analyze-button', 'disabled', allow_duplicate=True),
     Output('analyze-button', 'children', allow_duplicate=True)],
    Input('analyze-button', 'n_clicks'),
    State('uploaded-files-store', 'data'),
    prevent_initial_call=True
)
def perform_analysis(n_clicks, files_info) -> (Any, Any, Dict, bool, List):
    if not n_clicks or not files_info:
        raise PreventUpdate

    # Default to full analysis
    analysis_type = 'full'

    # Show progress indicator with loading state
    progress = html.Div([
        html.Div([
            html.I(className="fas fa-sync fa-spin", style={'fontSize': '32px', 'color': COLORS['primary'], 'marginBottom': '16px'}),
            html.H5("Analyzing with AI Agents", style={'color': COLORS['text_primary'], 'marginBottom': '8px', 'fontWeight': '600'}),
            html.P("This may take up to 10 minutes. Please wait while our agents process your files...",
                  style={'color': COLORS['text_muted'], 'fontSize': '14px', 'marginBottom': '16px'}),
            dbc.Progress(value=100, animated=True, striped=True, color="primary",
                        style={'height': '8px', 'marginBottom': '8px'}),
        ], style={'textAlign': 'center', 'padding': '60px 20px'})
    ], className='glass-panel')
    
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
        response = requests.post(f"{API_URL}{endpoint}", files=files_to_upload, timeout=600)

        if response.status_code == 200:
            data = response.json()
            results = create_professional_results(data, analysis_type)
            # Re-enable button after success
            button_content = [html.I(className="fas fa-robot me-2"), "Start Analysis"]
            return results, None, data, False, button_content
        else:
            error = dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Analysis failed: {response.text}"
            ], color="danger", style={'borderRadius': '12px'})
            # Re-enable button after error
            button_content = [html.I(className="fas fa-robot me-2"), "Start Analysis"]
            return error, None, {}, False, button_content

    except Exception as e:
        error = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error: {str(e)}"
        ], color="warning", style={'borderRadius': '12px'})
        # Re-enable button after error
        button_content = [html.I(className="fas fa-robot me-2"), "Start Analysis"]
        return error, None, {}, False, button_content

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
    
    # Add Contact button inside the Questions tab content
    components.extend([
        html.Div([
            dbc.Button(
                [html.I(className="fas fa-envelope me-2"), "Contact Founder"],
                id="contact-founder-button",
                color="primary",
                style={'marginTop': '20px'}
            )
        ], style={'textAlign': 'center'})
        ,
        html.Div(id='contact-founder-alert', style={'marginTop': '20px'})
    ])

    return html.Div([
        dcc.Store(id='email-data-store', data={
            'to_email': 'foresvest@gmail.com',
            'subject': 'Discussion about Questionnaire',
            'body': 'Dear Founder,\n\nI would like to schedule a time to discuss the questionnaire and request for some documents. Please let us know what time works for you.\n\nBest regards,'
        }),
        html.H4("Due Diligence Questions", 
               style={'color': '#FFFFFF', 'marginBottom': '24px', 'fontWeight': '600'}),
        html.Div(components if components else 
                [html.P("No questions generated", style={'color': '#6C7293'})])
    ], style={'padding': '20px'})

# ==================== SAVED ANALYSES CALLBACKS ====================

@app.callback(
    Output('saved-analyses-list', 'children'),
    [Input('refresh-analyses-btn', 'n_clicks'),
     Input('url', 'pathname')],  # Load on page load
    prevent_initial_call=False
)
def load_saved_analyses(n_clicks, pathname):
    """Load and display list of saved analyses."""
    try:
        response = requests.get(f"{API_URL}/analyses", timeout=15)
        if response.status_code == 200:
            data = response.json()
            analyses = data.get('analyses', [])

            if not analyses:
                return html.Div([
                    html.I(className="fas fa-inbox", style={'fontSize': '32px', 'color': COLORS['text_muted'], 'display': 'block', 'textAlign': 'center', 'marginBottom': '12px'}),
                    html.P("No saved analyses",
                          style={'color': COLORS['text_muted'], 'textAlign': 'center', 'fontSize': '13px', 'marginBottom': '0'})
                ], style={'padding': '24px 0', 'textAlign': 'center'})

            # Create compact cards for sidebar
            cards = []
            for analysis in analyses[:10]:  # Show max 10 recent
                # Format timestamp
                timestamp = datetime.fromisoformat(analysis['timestamp']).strftime('%b %d')

                # Get recommendation color
                recommendation = analysis.get('recommendation', 'Unknown')
                rec_color = {
                    'Strong Buy': COLORS['success'],
                    'Buy': COLORS['info'],
                    'Hold': COLORS['warning'],
                    'Pass': COLORS['danger']
                }.get(recommendation, COLORS['text_muted'])

                score = analysis.get('scores', {}).get('overall_weighted', 0)

                card = html.Div([
                    # Click area to load
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span(analysis['company_name'],
                                        className='company-name',
                                        style={'color': COLORS['text_primary'], 'fontSize': '13px', 'fontWeight': '600', 'display': 'block', 'marginBottom': '4px', 'whiteSpace': 'normal', 'wordBreak': 'break-word', 'lineHeight': '1.3'}),
                                html.Div([
                                    html.Span(timestamp, className='text-truncate', style={'color': COLORS['text_muted'], 'fontSize': '11px', 'marginRight': '8px'}),
                                    html.Span(f"{score:.0f}", style={'color': rec_color, 'fontSize': '11px', 'fontWeight': '600', 'flexShrink': '0'}),
                                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '6px', 'overflow': 'hidden'}),
                                html.Span(recommendation[:4],  # Abbreviate (Strong Buy -> Stro)
                                        className='recommendation-badge',
                                        style={
                                            'backgroundColor': f"{rec_color}20",
                                            'color': rec_color,
                                            'border': f"1px solid {rec_color}40",
                                            'padding': '2px 8px',
                                            'borderRadius': '4px',
                                            'fontSize': '10px',
                                            'fontWeight': '600',
                                            'display': 'inline-block'
                                        })
                            ])
                        ], id={'type': 'load-analysis-btn', 'index': analysis['id']},
                           style={'flex': '1', 'cursor': 'pointer'}),

                        # Delete button
                        html.Div([
                            html.I(className="fas fa-trash",
                                  id={'type': 'delete-analysis-btn', 'index': analysis['id']},
                                  style={'color': COLORS['text_muted'], 'fontSize': '12px', 'cursor': 'pointer', 'padding': '4px'})
                        ], style={'marginLeft': '8px'})

                    ], style={'display': 'flex', 'alignItems': 'flex-start', 'padding': '12px', 'background': COLORS['surface'], 'border': f"1px solid {COLORS['border']}", 'borderRadius': '8px', 'marginBottom': '8px', 'transition': 'all 0.2s ease'}),

                ], className='analysis-card')

                cards.append(card)

            return html.Div(cards)

        else:
            return html.Div([
                html.P(f"Failed to load analyses: {response.status_code}",
                      style={'color': COLORS['danger']})
            ])

    except Exception as e:
        return html.Div([
            html.P(f"Error loading analyses: {str(e)}",
                  style={'color': COLORS['danger']})
        ])


@app.callback(
    Output('analysis-results', 'children', allow_duplicate=True),
    Output('analysis-result-store', 'data', allow_duplicate=True),
    Input({'type': 'load-analysis-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def load_analysis_detail(n_clicks_list) -> (Any, Dict):
    """Load detailed analysis when user clicks on a saved analysis."""
    if not any(n_clicks_list):
        raise PreventUpdate

    # Get which button was clicked
    triggered = ctx.triggered_id
    if not triggered:
        raise PreventUpdate

    analysis_id = triggered['index']

    try:
        response = requests.get(f"{API_URL}/analyses/{analysis_id}", timeout=20)
        if response.status_code == 200:
            data = response.json()

            # Render analysis results using existing function
            results_div = create_professional_results(data, 'full')

            return results_div, data
        else:
            return html.Div([
                dbc.Alert(f"Failed to load analysis: {response.status_code}", color="danger")
            ]), {}

    except Exception as e:
        return html.Div([
            dbc.Alert(f"Error loading analysis: {str(e)}", color="danger")
        ]), {}


@app.callback(
    Output('saved-analyses-list', 'children', allow_duplicate=True),
    Input({'type': 'delete-analysis-btn', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def delete_analysis(n_clicks_list) -> html.Div:
    """Delete an analysis when delete button is clicked."""
    if not any(n_clicks_list):
        raise PreventUpdate

    # Get which button was clicked
    triggered = ctx.triggered_id
    if not triggered:
        raise PreventUpdate

    analysis_id = triggered['index']

    try:
        response = requests.delete(f"{API_URL}/analyses/{analysis_id}", timeout=15)
        if response.status_code == 200:
            # Reload the list after deletion
            response = requests.get(f"{API_URL}/analyses", timeout=15)
            if response.status_code == 200:
                data = response.json()
                analyses = data.get('analyses', [])

                if not analyses:
                    return html.Div([
                        html.P([
                            html.I(className="fas fa-inbox", style={'fontSize': '48px', 'color': '#6C7293', 'marginBottom': '16px'}),
                        ], style={'textAlign': 'center'}),
                        html.P("No saved analyses yet.",
                              style={'color': '#6C7293', 'textAlign': 'center'})
                    ], style={'padding': '40px 20px'})

                # Re-render the list (same logic as load_saved_analyses)
                # ... (simplified for brevity - will show success message)
                return html.Div([
                    dbc.Alert("Analysis deleted successfully. Please refresh the page.", color="success", dismissable=True)
                ])
        else:
            return html.Div([
                dbc.Alert(f"Failed to delete analysis: {response.status_code}", color="danger", dismissable=True)
            ])

    except Exception as e:
        return html.Div([
            dbc.Alert(f"Error deleting analysis: {str(e)}", color="danger", dismissable=True)
        ])




# ==================== CONTACT FOUNDER CALLBACKS ====================

@app.callback(
    Output('contact-founder-alert', 'children'),
    Input('contact-founder-button', 'n_clicks'),
    State('analysis-result-store', 'data'),
    prevent_initial_call=True
)
def contact_founder_callback(n_clicks, analysis_data):
    if not n_clicks:
        raise PreventUpdate#

    if not analysis_data:
        return dbc.Alert("No analysis data loaded. Please perform an analysis first.", color="warning", dismissable=True, duration=5000)

    contact_details = analysis_data.get("contact_details", {})
    email = contact_details.get("email")
    phone = contact_details.get("phone")

    if email:
        # If email exists, proceed with sending the email
        email_data = {
            'to_email': email,
            'subject': f'Request to Schedule an Interview Call with {analysis_data.get("company_name", "your company")}',
            'body': 'Dear Founder,\n\nWe hope you’re doing well.Based on our recent analysis of your company documents, we would like to request an interview call to align on next steps, share insights, and validate our direction before moving forward.\n\nAdditionally, I’d like to discuss the questionnaire and request a few supporting documents.Please let us know a convenient time slot for the discussion, and I will make the necessary arrangements accordingly.\n\nBest regards,\n Foresvest Team'
        }
        try:
            response = requests.post(f"{API_URL}/contact_founder", json=email_data, timeout=30)
            if response.status_code == 200:
                return dbc.Alert(f"Email sent successfully to {email}!", color="success", dismissable=True, duration=5000)
            else:
                return dbc.Alert(f"Failed to send email: {response.text}", color="danger", dismissable=True, duration=5000)
        except Exception as e:
            return dbc.Alert(f"Error sending email: {str(e)}", color="warning", dismissable=True, duration=5000)
    elif phone:
        # If no email but phone exists, show the phone number
        return dbc.Alert(f"No email found. Founder's phone number: {phone}", color="info", dismissable=True, duration=10000)
    else:
        # If neither exists, show a not found message
        return html.Div([
            dbc.Alert("No contact details (email or phone) found in the Document.", color="warning", dismissable=True),
            dbc.InputGroup([
                dbc.Input(id="manual-email-input", placeholder="Enter founder's email manually", type="email"),
                dbc.Button("Send Email", id="manual-send-email-button", color="primary"),
            ], className="mt-2")
        ])


@app.callback(
    Output('contact-founder-alert', 'children', allow_duplicate=True),
    Input('manual-send-email-button', 'n_clicks'),
    [State('manual-email-input', 'value'),
     State('analysis-result-store', 'data')],
    prevent_initial_call=True
)
def send_manual_email_callback(n_clicks, manual_email, analysis_data):
    if not n_clicks or not manual_email:
        raise PreventUpdate

    if not analysis_data:
        return dbc.Alert("Analysis data lost. Please try again.", color="danger", dismissable=True, duration=5000)

    # Basic email validation
    if "@" not in manual_email or "." not in manual_email:
        return dbc.Alert("Please enter a valid email address.", color="warning", dismissable=True, duration=5000)

    email_data = {
        'to_email': manual_email,
        'subject': f'Request to Schedule an Interview Call with {analysis_data.get("company_name", "your company")}',
        'body': 'Dear Founder,\n\nWe hope you’re doing well.Based on our recent analysis of your company documents, we would like to request an interview call to align on next steps, share insights, and validate our direction before moving forward.\n\nAdditionally, I’d like to discuss the questionnaire and request a few supporting documents.Please let us know a convenient time slot for the discussion, and I will make the necessary arrangements accordingly.\n\nBest regards,\nForesvest Team'
    }
    try:
        response = requests.post(f"{API_URL}/contact_founder", json=email_data, timeout=30)
        if response.status_code == 200:
            return dbc.Alert(f"Email sent successfully to {manual_email}!", color="success", dismissable=True, duration=5000)
        else:
            return dbc.Alert(f"Failed to send email: {response.text}", color="danger", dismissable=True, duration=5000)
    except Exception as e:
        return dbc.Alert(f"Error sending email: {str(e)}", color="warning", dismissable=True, duration=5000)


# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)