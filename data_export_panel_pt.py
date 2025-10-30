"""
Módulo do Painel de Exportação de Dados
Fornece UI para exportar e gerenciar dados históricos
"""

import streamlit as st
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime
from data_logger import DataLogger
from config_manager import ConfigManager

def show_data_export_panel(logger: DataLogger, config: ConfigManager):
    """Exibir painel de exportação e gerenciamento de dados"""
    st.title("📥 Exportação e Gerenciamento de Dados")
    st.markdown("Exporte dados históricos de temperatura e gerencie arquivos de log")
    
    # Visão Geral de Estatísticas
    st.subheader("📊 Estatísticas de Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hours_range = st.selectbox(
            "Intervalo de Tempo para Estatísticas",
            [6, 12, 24, 48, 72, 168],
            index=2,
            format_func=lambda x: f"Últimas {x} horas" if x < 168 else "Última semana"
        )
    
    with col2:
        if st.button("Calcular Estatísticas", key="calc_stats"):
            stats = logger.get_statistics(hours_range)
            if stats:
                st.session_state.current_stats = stats
            else:
                st.warning("Nenhum dado disponível para o intervalo selecionado")
    
    if hasattr(st.session_state, 'current_stats') and st.session_state.current_stats:
        stats = st.session_state.current_stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Leituras", stats.get('total_readings', 0))
            st.metric("Eventos Críticos", stats.get('critical_events', 0))
        
        with col2:
            evap_stats = stats.get('evaporator', {})
            st.metric("Média Evaporador", f"{evap_stats.get('mean', 0):.2f}°C")
            st.metric("Faixa Evaporador", 
                     f"{evap_stats.get('min', 0):.2f}°C a {evap_stats.get('max', 0):.2f}°C")
        
        with col3:
            cond_stats = stats.get('condenser', {})
            st.metric("Média Condensador", f"{cond_stats.get('mean', 0):.2f}°C")
            st.metric("Eventos de Aviso", stats.get('warning_events', 0))
    
    st.markdown("---")
    
    # Seção de Exportação de Dados
    st.subheader("💾 Exportar Dados de Temperatura")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_hours = st.number_input(
            "Horas de Dados para Exportar",
            min_value=1,
            max_value=720,
            value=24,
            step=1,
            help="Número de horas de dados históricos para exportar"
        )
    
    with col2:
        export_filename = st.text_input(
            "Nome do Arquivo de Exportação",
            value=f"exportacao_temperatura_{datetime.now(ZoneInfo("America/Sao_Paulo"))
.strftime('%Y%m%d_%H%M%S')}.csv",
            help="Nome para o arquivo CSV exportado"
        )
    
    if st.button("Exportar para CSV", key="export_csv"):
        export_path = f"exports/{export_filename}"
        if logger.export_data(export_path, hours=export_hours):
            st.success(f"✓ Dados exportados com sucesso para {export_path}")
            try:
                with open(export_path, 'r') as f:
                    csv_data = f.read()
                st.download_button(
                    label="Baixar Arquivo Exportado",
                    data=csv_data,
                    file_name=export_filename,
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Erro ao preparar download: {e}")
        else:
            st.error("Falha ao exportar dados")
    
    st.markdown("---")
    
    # Visualizar Dados Históricos
    st.subheader("📋 Visualizar Dados Históricos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        view_hours = st.number_input(
            "Horas de Dados para Visualizar",
            min_value=1,
            max_value=72,
            value=6,
            step=1,
            key="view_hours"
        )
    
    with col2:
        if st.button("Carregar Dados Históricos", key="load_historical"):
            df = logger.get_historical_data(hours=view_hours)
            if not df.empty:
                st.session_state.historical_df = df
                st.success(f"Carregados {len(df)} registros")
            else:
                st.warning("Nenhum dado disponível para o intervalo selecionado")
    
    if hasattr(st.session_state, 'historical_df') and not st.session_state.historical_df.empty:
        df = st.session_state.historical_df
        display_df = df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(display_df, use_container_width=True, height=400)
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Baixar Visualização Atual como CSV",
            data=csv,
            file_name=f"dados_historicos_{datetime.now(ZoneInfo("America/Sao_Paulo"))
.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    
    # Gerenciamento de Dados
    st.subheader("🗑️ Gerenciamento de Dados")
    st.warning("⚠️ Operações de gerenciamento de dados são permanentes e não podem ser desfeitas!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Limpar Dados Antigos**")
        st.info(f"Período de retenção atual: {config.get('data_logging', 'retention_days')} dias")
        if st.button("Limpar Registros Antigos", key="cleanup_data"):
            if st.checkbox("Confirmar limpeza de registros antigos", key="confirm_cleanup"):
                records_removed = logger.cleanup_old_data()
                if records_removed > 0:
                    st.success(f"✓ Removidos {records_removed} registros antigos")
                else:
                    st.info("Nenhum registro antigo para remover")
    
    with col2:
        st.markdown("**Limpar Todos os Dados**")
        st.error("Isso deletará TODOS os dados históricos!")
        if st.button("Limpar Todos os Dados", key="clear_all_data"):
            confirm_text = st.text_input(
                "Digite 'DELETAR TUDO' para confirmar",
                key="confirm_delete_text"
            )
            if confirm_text == "DELETAR TUDO":
                if logger.clear_all_data():
                    st.success("✓ Todos os dados foram limpos")
                    if hasattr(st.session_state, 'historical_df'):
                        del st.session_state.historical_df
                    if hasattr(st.session_state, 'current_stats'):
                        del st.session_state.current_stats
                    st.rerun()
                else:
                    st.error("Falha ao limpar dados")
