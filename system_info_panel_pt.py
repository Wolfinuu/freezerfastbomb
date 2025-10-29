"""
Módulo do Painel de Informações do Sistema
Exibe status do sistema, diagnósticos e informações
"""

import streamlit as st
from datetime import datetime
import os
from config_manager import ConfigManager
from data_simulator import TemperatureSimulator
from email_notifier import EmailNotifier
from data_logger import DataLogger

def show_system_info_panel(config: ConfigManager, simulator: TemperatureSimulator, 
                           notifier: EmailNotifier, logger: DataLogger):
    """Exibir informações do sistema e diagnósticos"""
    st.title("ℹ️ Informações do Sistema")
    st.markdown("Status do sistema, diagnósticos e informações técnicas")
    
    # Status do Sistema
    st.subheader("🔌 Status do Sistema")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Configuração", "✓ Carregada")
        config_file_exists = os.path.exists('freezer_config.json')
        st.metric("Arquivo de Config", "✓ Encontrado" if config_file_exists else "✗ Não Encontrado")
    
    with col2:
        csv_path = config.get('data_logging', 'csv_file_path')
        csv_exists = os.path.exists(csv_path)
        st.metric("Logger de Dados", "✓ Ativo" if csv_exists else "⚠ Sem Dados Ainda")
        if csv_exists:
            file_size = os.path.getsize(csv_path)
            st.metric("Tamanho do Arquivo de Log", f"{file_size / 1024:.2f} KB")
    
    with col3:
        email_configured = (
            config.get('email_config', 'sender_email') and
            os.environ.get('SMTP_PASSWORD') and
            len(config.get('email_config', 'recipient_emails')) > 0
        )
        st.metric("Alertas por E-mail", "✓ Configurado" if email_configured else "⚠ Não Configurado")
        st.metric("Simulador", "✓ Rodando")
    
    st.markdown("---")
    
    # Informações do Freezer
    st.subheader("🏭 Informações do Freezer")
    info_data = {
        "Modelo": config.get('freezer_info', 'model_name'),
        "Localização": config.get('freezer_info', 'location'),
        "Operador": config.get('freezer_info', 'operator_name'),
        "Contato": config.get('freezer_info', 'operator_contact'),
    }
    for label, value in info_data.items():
        st.text(f"{label}: {value}")
    
    st.markdown("---")
    
    # Resumo da Configuração
    st.subheader("⚙️ Resumo da Configuração")
    config_tabs = st.tabs(["Limites de Temperatura", "Coleta de Dados", "Alertas", "Registro"])
    
    with config_tabs[0]:
        st.markdown("**Zona do Evaporador**")
        evap = config.get('temperature_thresholds', 'evaporator')
        st.text(f"Faixa Normal: {evap['min']}°C a {evap['max']}°C")
        st.text(f"Limites Críticos: {evap['critical_low']}°C a {evap['critical_high']}°C")
        st.markdown("**Zona do Condensador**")
        cond = config.get('temperature_thresholds', 'condenser')
        st.text(f"Faixa Normal: {cond['min']}°C a {cond['max']}°C")
        st.text(f"Limites Críticos: {cond['critical_low']}°C a {cond['critical_high']}°C")
        st.markdown("**Zona Ambiente**")
        amb = config.get('temperature_thresholds', 'ambient')
        st.text(f"Faixa Normal: {amb['min']}°C a {amb['max']}°C")
        st.text(f"Limites Críticos: {amb['critical_low']}°C a {amb['critical_high']}°C")
    
    with config_tabs[1]:
        st.text(f"Intervalo de Leitura: {config.get('data_collection', 'reading_interval_seconds')} segundos")
        st.text(f"Intervalo de Atualização: {config.get('data_collection', 'chart_refresh_interval_seconds')} segundos")
        st.text(f"Pontos de Dados do Gráfico: {config.get('data_collection', 'max_data_points_display')}")
    
    with config_tabs[2]:
        alerts_enabled = "Ativado" if config.get('alert_settings', 'enable_email_alerts') else "Desativado"
        st.text(f"Alertas por E-mail: {alerts_enabled}")
        st.text(f"Tempo de Espera de Alerta: {config.get('alert_settings', 'alert_cooldown_seconds')} segundos")
        st.text(f"Limite de Acionamento: {config.get('alert_settings', 'consecutive_readings_trigger')} leituras")
        if email_configured:
            st.text(f"Servidor SMTP: {config.get('email_config', 'smtp_server')}:{config.get('email_config', 'smtp_port')}")
            st.text(f"Remetente: {config.get('email_config', 'sender_email')}")
            st.text(f"Destinatários: {len(config.get('email_config', 'recipient_emails'))}")
    
    with config_tabs[3]:
        logging_enabled = "Ativado" if config.get('data_logging', 'enable_csv_logging') else "Desativado"
        st.text(f"Registro CSV: {logging_enabled}")
        st.text(f"Arquivo de Log: {config.get('data_logging', 'csv_file_path')}")
        st.text(f"Retenção: {config.get('data_logging', 'retention_days')} dias")
    
    st.markdown("---")
    
    # Status do Simulador
    st.subheader("🔬 Status do Simulador")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text(f"Modo de Falha: {'Ativo' if simulator.failure_mode else 'Inativo'}")
        st.text(f"Probabilidade de Falha: {config.get('simulation', 'failure_probability') * 100}%")
        st.text(f"Duração da Falha: {config.get('simulation', 'failure_duration_seconds')}s")
    
    with col2:
        st.text(f"Faixa Normal: {config.get('simulation', 'normal_temp_evaporator_min')}°C a {config.get('simulation', 'normal_temp_evaporator_max')}°C")
        st.text(f"Variação de Temperatura: ±{config.get('simulation', 'temp_variation_range')}°C")
    
    st.markdown("**Últimas Temperaturas Registradas:**")
    for zone, temp in simulator.last_temperatures.items():
        zone_names = {'evaporator': 'Evaporador', 'condenser': 'Condensador', 'ambient': 'Ambiente'}
        st.text(f"{zone_names.get(zone, zone.capitalize())}: {temp:.2f}°C")
    
    if st.button("Redefinir Simulador", key="reset_simulator"):
        simulator.reset_simulator()
        st.success("✓ Simulador redefinido para estado inicial")
    
    st.markdown("---")
    
    # Diagnósticos do Sistema
    st.subheader("🔍 Diagnósticos do Sistema")
    diagnostics = {
        "Arquivo de Config": "✓ OK" if os.path.exists('freezer_config.json') else "✗ Ausente",
        "Diretório de Dados": "✓ OK" if os.path.exists('data') else "⚠ Não Criado",
        "Diretório de Exportação": "✓ OK" if os.path.exists('exports') else "⚠ Não Criado",
        "Arquivo de Log CSV": "✓ OK" if csv_exists else "⚠ Não Criado",
    }
    
    for check, status in diagnostics.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(check)
        with col2:
            if "✓" in status:
                st.success(status)
            elif "⚠" in status:
                st.warning(status)
            else:
                st.error(status)
    
    st.markdown("---")
    
    # Seção Sobre
    st.subheader("📖 Sobre")
    st.markdown("""
    **FAST BOMBAS - Sistema de Controle Térmico de Freezer**
    
    Versão: 1.0.0
    
    Um sistema de monitoramento abrangente baseado em Python para freezers industriais com:
    - Monitoramento de temperatura em tempo real em múltiplas zonas
    - Alertas automáticos por e-mail para condições críticas
    - Registro e exportação de dados históricos
    - Limites e configurações totalmente personalizáveis
    - Interface de dashboard profissional construída com Streamlit
    
    **Componentes:**
    - Gerenciador de Configuração: Gerencia todas as configurações do sistema com persistência JSON
    - Simulador de Dados: Gera dados de temperatura realistas para testes
    - Notificador de E-mail: Envia alertas automatizados via SMTP
    - Logger de Dados: Gerencia registro CSV e dados históricos
    - Dashboard: Interface web interativa para monitoramento e controle
    
    **Requisitos do Sistema:**
    - Python 3.11+
    - Streamlit
    - Plotly
    - Pandas
    
    ---
    
    *Desenvolvido para monitoramento de freezers industriais FAST BOMBAS*
    """)
    
    st.markdown("---")
    
    # Metadados do Sistema
    with st.expander("📋 Metadados do Sistema"):
        metadata = config.get('system_metadata')
        st.json(metadata)
