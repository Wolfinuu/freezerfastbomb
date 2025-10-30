"""
FAST BOMBAS - Sistema de Controle Térmico de Freezer
Aplicação Principal do Dashboard Streamlit
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import time
import pandas as pd

from config_manager import ConfigManager
from data_simulator import TemperatureSimulator
from email_notifier import EmailNotifier
from data_logger import DataLogger

# Configuração da página
st.set_page_config(
    page_title="FAST BOMBAS - Controle de Freezer",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhor estilização
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .status-ok {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-critical {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado da sessão
def initialize_session_state():
    """Inicializar todas as variáveis de estado da sessão"""
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    if 'simulator' not in st.session_state:
        st.session_state.simulator = TemperatureSimulator(st.session_state.config_manager)
    
    if 'notifier' not in st.session_state:
        st.session_state.notifier = EmailNotifier(st.session_state.config_manager)
    
    if 'logger' not in st.session_state:
        st.session_state.logger = DataLogger(st.session_state.config_manager)
    
    if 'current_reading' not in st.session_state:
        st.session_state.current_reading = None
    
    if 'current_status' not in st.session_state:
        st.session_state.current_status = None
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now(ZoneInfo("America/Sao_Paulo"))

initialize_session_state()

# Obter referências para objetos da sessão
config = st.session_state.config_manager
simulator = st.session_state.simulator
notifier = st.session_state.notifier
logger = st.session_state.logger

def create_gauge_chart(value: float, title: str, min_val: float, max_val: float, 
                       critical_low: float, critical_high: float, 
                       normal_min: float, normal_max: float) -> go.Figure:
    """
    Criar gráfico de medidor para exibição de temperatura
    """
    # Determinar cor baseada no valor
    if value < critical_low or value > critical_high:
        color = "#dc3545"  # Vermelho para crítico
    elif value < normal_min or value > normal_max:
        color = "#ffc107"  # Amarelo para aviso
    else:
        color = "#28a745"  # Verde para OK
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 20}},
        number={'suffix': "°C", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_val, critical_low], 'color': '#ffebee'},
                {'range': [critical_low, normal_min], 'color': '#fff9c4'},
                {'range': [normal_min, normal_max], 'color': '#e8f5e9'},
                {'range': [normal_max, critical_high], 'color': '#fff9c4'},
                {'range': [critical_high, max_val], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': critical_high
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#333", 'family': "Arial"}
    )
    
    return fig

def create_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Criar gráfico de tendência para histórico de temperatura
    """
    fig = go.Figure()
    
    if not df.empty:
        # Temperatura do evaporador
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['evaporator_temp'],
            mode='lines+markers',
            name='Evaporador',
            line=dict(color='#2196f3', width=2),
            marker=dict(size=6)
        ))
        
        # Temperatura do condensador
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['condenser_temp'],
            mode='lines+markers',
            name='Condensador',
            line=dict(color='#ff9800', width=2),
            marker=dict(size=6)
        ))
        
        # Temperatura ambiente
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ambient_temp'],
            mode='lines+markers',
            name='Ambiente',
            line=dict(color='#4caf50', width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Tendência de Temperatura (Últimas 30 Leituras)",
        xaxis_title="Hora",
        yaxis_title="Temperatura (°C)",
        hovermode='x unified',
        height=400,
        margin=dict(l=50, r=20, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )
    
    return fig

def get_status_badge(status: str) -> str:
    """
    Obter badge HTML para status
    """
    if status == 'OK':
        return '<span class="status-ok">✓ OK</span>'
    elif status == 'WARNING':
        return '<span class="status-warning">⚠ AVISO</span>'
    else:
        return '<span class="status-critical">🚨 CRÍTICO</span>'

def update_data():
    """Atualizar leitura de temperatura e processar alertas"""
    # Obter nova leitura
    reading = simulator.get_reading()
    status = simulator.get_status(reading)
    
    # Registrar a leitura
    logger.log_reading(reading, status)
    
    # Verificar status crítico e enviar alerta
    if status['overall'] == 'CRITICAL':
        notifier.send_alert(reading, status)
    
    # Atualizar estado da sessão
    st.session_state.current_reading = reading
    st.session_state.current_status = status
    st.session_state.last_update = datetime.now(ZoneInfo("America/Sao_Paulo"))

# Dashboard Principal
def main_dashboard():
    """Página principal do dashboard"""
    
    # Cabeçalho
    dashboard_title = config.get('ui_settings', 'dashboard_title')
    st.markdown(f'<div class="main-header">❄️ {dashboard_title}</div>', unsafe_allow_html=True)
    
    # Atualizar dados
    update_data()
    
    reading = st.session_state.current_reading
    status = st.session_state.current_status
    
    if reading is None or status is None:
        st.warning("Aguardando dados...")
        return
    
    # Visão Geral do Status do Sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status do Sistema", status['overall'], 
                 delta="Ativo" if status['overall'] == 'OK' else "Alerta")
    
    with col2:
        st.metric("Última Atualização", 
                 st.session_state.last_update.strftime("%H:%M:%S"))
    
    with col3:
        freezer_location = config.get('freezer_info', 'location')
        st.metric("Localização", freezer_location)
    
    with col4:
        if reading.get('failure_mode', False):
            st.metric("Modo", "SIMULAÇÃO DE FALHA", delta="Aviso", delta_color="inverse")
        else:
            st.metric("Modo", "Operação Normal", delta="OK")
    
    st.markdown("---")
    
    # Medidores de Temperatura
    st.subheader("📊 Leituras de Temperatura Atual")
    
    col1, col2, col3 = st.columns(3)
    
    # Medidor do evaporador
    with col1:
        evap_thresholds = config.get('temperature_thresholds', 'evaporator')
        fig_evap = create_gauge_chart(
            reading['evaporator_temp'],
            "Zona do Evaporador",
            evap_thresholds['critical_low'] - 5,
            evap_thresholds['critical_high'] + 5,
            evap_thresholds['critical_low'],
            evap_thresholds['critical_high'],
            evap_thresholds['min'],
            evap_thresholds['max']
        )
        st.plotly_chart(fig_evap, width='stretch')
        st.markdown(f"Status: {get_status_badge(status['evaporator'])}", unsafe_allow_html=True)
    
    # Medidor do condensador
    with col2:
        cond_thresholds = config.get('temperature_thresholds', 'condenser')
        fig_cond = create_gauge_chart(
            reading['condenser_temp'],
            "Zona do Condensador",
            cond_thresholds['critical_low'] - 5,
            cond_thresholds['critical_high'] + 10,
            cond_thresholds['critical_low'],
            cond_thresholds['critical_high'],
            cond_thresholds['min'],
            cond_thresholds['max']
        )
        st.plotly_chart(fig_cond, width='stretch')
        st.markdown(f"Status: {get_status_badge(status['condenser'])}", unsafe_allow_html=True)
    
    # Medidor ambiente
    with col3:
        amb_thresholds = config.get('temperature_thresholds', 'ambient')
        fig_amb = create_gauge_chart(
            reading['ambient_temp'],
            "Zona Ambiente",
            amb_thresholds['critical_low'] - 5,
            amb_thresholds['critical_high'] + 5,
            amb_thresholds['critical_low'],
            amb_thresholds['critical_high'],
            amb_thresholds['min'],
            amb_thresholds['max']
        )
        st.plotly_chart(fig_amb, width='stretch')
        st.markdown(f"Status: {get_status_badge(status['ambient'])}", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráfico de Tendência de Temperatura
    st.subheader("📈 Histórico de Temperatura")
    
    max_points = config.get('data_collection', 'max_data_points_display')
    recent_df = logger.get_recent_readings(max_points)
    
    if not recent_df.empty:
        trend_fig = create_trend_chart(recent_df)
        st.plotly_chart(trend_fig, width='stretch')
    else:
        st.info("Nenhum dado histórico disponível ainda. Os dados aparecerão conforme as leituras forem coletadas.")
    
    # Histórico de Alertas
    if config.get('ui_settings', 'show_advanced_metrics'):
        st.markdown("---")
        st.subheader("🚨 Alertas Recentes")
        
        alerts = logger.get_alert_history(hours=2)
        
        if alerts:
            alert_df = pd.DataFrame(alerts)
            alert_df['timestamp'] = pd.to_datetime(alert_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(alert_df, width='stretch')
        else:
            st.success("Nenhum alerta nas últimas 2 horas - Sistema operando normalmente!")
    
    # Auto-atualização
    refresh_interval = config.get('data_collection', 'chart_refresh_interval_seconds')
    time.sleep(refresh_interval)
    st.rerun()

# Navegação da Barra Lateral
st.sidebar.title("🎛️ Navegação")
page = st.sidebar.radio("Selecionar Página", 
                        ["Painel de Controle", "Configuração", "Exportar Dados", "Informações do Sistema"])

if page == "Painel de Controle":
    main_dashboard()
    
elif page == "Configuração":
    from config_panel_pt import show_configuration_panel
    show_configuration_panel(config)
    
elif page == "Exportar Dados":
    from data_export_panel_pt import show_data_export_panel
    show_data_export_panel(logger, config)
    
elif page == "Informações do Sistema":
    from system_info_panel_pt import show_system_info_panel
    show_system_info_panel(config, simulator, notifier, logger)
