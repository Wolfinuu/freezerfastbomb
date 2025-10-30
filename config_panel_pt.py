"""
Módulo do Painel de Configuração
Fornece UI para ajustar todas as configurações do sistema
"""

import streamlit as st
from config_manager import ConfigManager
import os
from zoneinfo import ZoneInfo
from datetime import datetime

def show_configuration_panel(config: ConfigManager):
    """Exibir painel de configuração para todas as configurações do sistema"""
    st.title("⚙️ Configuração do Sistema")
    st.markdown("Personalize todas as configurações de monitoramento do freezer para atender seus requisitos específicos.")
    
    # Criar abas para diferentes seções de configuração
    tabs = st.tabs([
        "Info do Freezer",
        "Limites de Temperatura",
        "Coleta de Dados",
        "Alertas por E-mail",
        "Registro de Dados",
        "Simulação",
        "Avançado"
    ])
    
    # Aba 1: Informações do Freezer
    with tabs[0]:
        st.subheader("🏭 Informações do Freezer")
        st.markdown("Informações básicas sobre a instalação do seu freezer")
        
        model_name = st.text_input(
            "Nome do Modelo do Freezer",
            value=config.get('freezer_info', 'model_name'),
            help="Digite o nome do modelo ou identificador deste freezer"
        )
        
        location = st.text_input(
            "Local de Instalação",
            value=config.get('freezer_info', 'location'),
            help="Localização física onde o freezer está instalado"
        )
        
        operator_name = st.text_input(
            "Nome do Operador",
            value=config.get('freezer_info', 'operator_name'),
            help="Nome da pessoa ou equipe responsável"
        )
        
        operator_contact = st.text_input(
            "E-mail de Contato do Operador",
            value=config.get('freezer_info', 'operator_contact'),
            help="Endereço de e-mail do operador responsável"
        )
        
        if st.button("Salvar Info do Freezer", key="save_freezer_info"):
            config.set('freezer_info', 'model_name', model_name)
            config.set('freezer_info', 'location', location)
            config.set('freezer_info', 'operator_name', operator_name)
            config.set('freezer_info', 'operator_contact', operator_contact)
            st.success("✓ Informações do freezer salvas com sucesso!")
    
    # Aba 2: Limites de Temperatura
    with tabs[1]:
        st.subheader("🌡️ Limites de Temperatura")
        st.markdown("Configure os limites de temperatura para cada zona. Limites críticos acionam alertas.")
        
        # Zona do Evaporador
        st.markdown("**Zona do Evaporador**")
        col1, col2 = st.columns(2)
        with col1:
            evap_min = st.number_input(
                "Mín Normal (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'min')),
                step=0.5,
                key="evap_min"
            )
            evap_critical_low = st.number_input(
                "Crítico Baixo (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'critical_low')),
                step=0.5,
                key="evap_crit_low"
            )
        with col2:
            evap_max = st.number_input(
                "Máx Normal (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'max')),
                step=0.5,
                key="evap_max"
            )
            evap_critical_high = st.number_input(
                "Crítico Alto (°C)",
                value=float(config.get('temperature_thresholds', 'evaporator', 'critical_high')),
                step=0.5,
                key="evap_crit_high"
            )
        
        st.markdown("---")
        
        # Zona do Condensador
        st.markdown("**Zona do Condensador**")
        col1, col2 = st.columns(2)
        with col1:
            cond_min = st.number_input(
                "Mín Normal (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'min')),
                step=0.5,
                key="cond_min"
            )
            cond_critical_low = st.number_input(
                "Crítico Baixo (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'critical_low')),
                step=0.5,
                key="cond_crit_low"
            )
        with col2:
            cond_max = st.number_input(
                "Máx Normal (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'max')),
                step=0.5,
                key="cond_max"
            )
            cond_critical_high = st.number_input(
                "Crítico Alto (°C)",
                value=float(config.get('temperature_thresholds', 'condenser', 'critical_high')),
                step=0.5,
                key="cond_crit_high"
            )
        
        st.markdown("---")
        
        # Zona Ambiente
        st.markdown("**Zona Ambiente**")
        col1, col2 = st.columns(2)
        with col1:
            amb_min = st.number_input(
                "Mín Normal (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'min')),
                step=0.5,
                key="amb_min"
            )
            amb_critical_low = st.number_input(
                "Crítico Baixo (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'critical_low')),
                step=0.5,
                key="amb_crit_low"
            )
        with col2:
            amb_max = st.number_input(
                "Máx Normal (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'max')),
                step=0.5,
                key="amb_max"
            )
            amb_critical_high = st.number_input(
                "Crítico Alto (°C)",
                value=float(config.get('temperature_thresholds', 'ambient', 'critical_high')),
                step=0.5,
                key="amb_crit_high"
            )
        
        if st.button("Salvar Limites de Temperatura", key="save_temp_thresholds"):
            config.set('temperature_thresholds', 'evaporator', 'min', evap_min)
            config.set('temperature_thresholds', 'evaporator', 'max', evap_max)
            config.set('temperature_thresholds', 'evaporator', 'critical_low', evap_critical_low)
            config.set('temperature_thresholds', 'evaporator', 'critical_high', evap_critical_high)
            config.set('temperature_thresholds', 'condenser', 'min', cond_min)
            config.set('temperature_thresholds', 'condenser', 'max', cond_max)
            config.set('temperature_thresholds', 'condenser', 'critical_low', cond_critical_low)
            config.set('temperature_thresholds', 'condenser', 'critical_high', cond_critical_high)
            config.set('temperature_thresholds', 'ambient', 'min', amb_min)
            config.set('temperature_thresholds', 'ambient', 'max', amb_max)
            config.set('temperature_thresholds', 'ambient', 'critical_low', amb_critical_low)
            config.set('temperature_thresholds', 'ambient', 'critical_high', amb_critical_high)
            st.success("✓ Limites de temperatura salvos com sucesso!")
    
    # Aba 3: Coleta de Dados
    with tabs[2]:
        st.subheader("📡 Configurações de Coleta de Dados")
        st.markdown("Configure a frequência de coleta e exibição de dados")
        
        reading_interval = st.number_input(
            "Intervalo de Leitura (segundos)",
            min_value=1,
            max_value=60,
            value=config.get('data_collection', 'reading_interval_seconds'),
            help="Com que frequência coletar leituras de temperatura"
        )
        
        refresh_interval = st.number_input(
            "Intervalo de Atualização do Dashboard (segundos)",
            min_value=1,
            max_value=60,
            value=config.get('data_collection', 'chart_refresh_interval_seconds'),
            help="Com que frequência atualizar a exibição do dashboard"
        )
        
        max_points = st.number_input(
            "Máximo de Pontos de Dados no Gráfico",
            min_value=10,
            max_value=100,
            value=config.get('data_collection', 'max_data_points_display'),
            help="Número de leituras recentes a mostrar nos gráficos de tendência"
        )
        
        if st.button("Salvar Configurações de Coleta", key="save_data_collection"):
            config.set('data_collection', 'reading_interval_seconds', reading_interval)
            config.set('data_collection', 'chart_refresh_interval_seconds', refresh_interval)
            config.set('data_collection', 'max_data_points_display', max_points)
            st.success("✓ Configurações de coleta salvas com sucesso!")
    
    # Aba 4: Alertas por E-mail
    with tabs[3]:
        st.subheader("📧 Configuração de Alertas por E-mail")
        st.markdown("Configure notificações automáticas por e-mail para eventos críticos")
        
        enable_email = st.checkbox(
            "Ativar Alertas por E-mail",
            value=config.get('alert_settings', 'enable_email_alerts'),
            help="Ativar ou desativar notificações por e-mail"
        )
        
        alert_cooldown = st.number_input(
            "Período de Espera entre Alertas (segundos)",
            min_value=60,
            max_value=3600,
            value=config.get('alert_settings', 'alert_cooldown_seconds'),
            step=60,
            help="Tempo mínimo entre alertas repetidos"
        )
        
        consecutive_readings = st.number_input(
            "Leituras Críticas Consecutivas para Acionar Alerta",
            min_value=1,
            max_value=10,
            value=config.get('alert_settings', 'consecutive_readings_trigger'),
            help="Número de leituras críticas consecutivas antes de enviar alerta"
        )
        
        st.markdown("---")
        st.markdown("**Configuração SMTP**")
        
        smtp_server = st.text_input(
            "Servidor SMTP",
            value=config.get('email_config', 'smtp_server'),
            help="Endereço do servidor SMTP (ex: smtp.gmail.com)"
        )
        
        smtp_port = st.number_input(
            "Porta SMTP",
            min_value=1,
            max_value=65535,
            value=config.get('email_config', 'smtp_port'),
            help="Porta SMTP (geralmente 587 para TLS)"
        )
        
        sender_email = st.text_input(
            "Endereço de E-mail Remetente",
            value=config.get('email_config', 'sender_email'),
            help="Endereço de e-mail para enviar alertas"
        )
        
        st.info("🔒 A senha SMTP deve ser definida como variável de ambiente 'SMTP_PASSWORD' por segurança. Nunca armazene senhas em arquivos de configuração!")
        
        password_status = "✓ Senha configurada no ambiente" if os.environ.get('SMTP_PASSWORD') else "⚠ Senha não encontrada no ambiente"
        st.text(password_status)
        
        use_tls = st.checkbox(
            "Usar Criptografia TLS",
            value=config.get('email_config', 'use_tls'),
            help="Ativar TLS para transmissão segura de e-mail"
        )
        
        recipient_emails_text = st.text_area(
            "Endereços de E-mail Destinatários (um por linha)",
            value='\n'.join(config.get('email_config', 'recipient_emails')),
            help="Digite endereços de e-mail para receber alertas, um por linha"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Salvar Configuração de E-mail", key="save_email_config"):
                config.set('alert_settings', 'enable_email_alerts', enable_email)
                config.set('alert_settings', 'alert_cooldown_seconds', alert_cooldown)
                config.set('alert_settings', 'consecutive_readings_trigger', consecutive_readings)
                config.set('email_config', 'smtp_server', smtp_server)
                config.set('email_config', 'smtp_port', smtp_port)
                config.set('email_config', 'sender_email', sender_email)
                config.set('email_config', 'use_tls', use_tls)
                recipients = [email.strip() for email in recipient_emails_text.split('\n') if email.strip()]
                config.set('email_config', 'recipient_emails', recipients)
                st.success("✓ Configuração de e-mail salva com sucesso!")
                st.info("Lembre-se: Defina a variável de ambiente SMTP_PASSWORD para ativar alertas por e-mail")
        
        with col2:
            if st.button("Testar Conexão de E-mail", key="test_email"):
                from email_notifier import EmailNotifier
                test_notifier = EmailNotifier(config)
                success, message = test_notifier.test_email_connection()
                if success:
                    st.success(f"✓ {message}")
                else:
                    st.error(f"✗ {message}")
    
    # Aba 5: Registro de Dados
    with tabs[4]:
        st.subheader("💾 Configurações de Registro de Dados")
        st.markdown("Configure como os dados de temperatura são registrados em arquivos")
        
        enable_logging = st.checkbox(
            "Ativar Registro em CSV",
            value=config.get('data_logging', 'enable_csv_logging'),
            help="Salvar todas as leituras em arquivo CSV"
        )
        
        csv_path = st.text_input(
            "Caminho do Arquivo CSV",
            value=config.get('data_logging', 'csv_file_path'),
            help="Caminho onde o arquivo de log CSV será salvo"
        )
        
        retention_days = st.number_input(
            "Período de Retenção de Dados (dias)",
            min_value=1,
            max_value=365,
            value=config.get('data_logging', 'retention_days'),
            help="Número de dias para manter dados históricos"
        )
        
        if st.button("Salvar Configurações de Registro", key="save_logging"):
            config.set('data_logging', 'enable_csv_logging', enable_logging)
            config.set('data_logging', 'csv_file_path', csv_path)
            config.set('data_logging', 'retention_days', retention_days)
            st.success("✓ Configurações de registro salvas com sucesso!")
    
    # Aba 6: Configurações de Simulação
    with tabs[5]:
        st.subheader("🔬 Configurações de Simulação")
        st.markdown("Configure o comportamento do simulador de temperatura (para testes)")
        
        st.info("Estas configurações controlam o gerador de dados de temperatura simulados usado para testar o sistema.")
        
        sim_min = st.number_input(
            "Temperatura Normal Mín (°C)",
            value=float(config.get('simulation', 'normal_temp_evaporator_min')),
            step=0.5,
            help="Temperatura operacional normal mínima para evaporador"
        )
        
        sim_max = st.number_input(
            "Temperatura Normal Máx (°C)",
            value=float(config.get('simulation', 'normal_temp_evaporator_max')),
            step=0.5,
            help="Temperatura operacional normal máxima para evaporador"
        )
        
        failure_prob = st.slider(
            "Probabilidade de Falha (%)",
            min_value=0.0,
            max_value=20.0,
            value=config.get('simulation', 'failure_probability') * 100,
            step=0.5,
            help="Probabilidade de simular um evento de falha por leitura"
        )
        
        failure_duration = st.number_input(
            "Duração da Falha (segundos)",
            min_value=10,
            max_value=600,
            value=config.get('simulation', 'failure_duration_seconds'),
            step=10,
            help="Quanto tempo dura uma falha simulada"
        )
        
        temp_variation = st.number_input(
            "Faixa de Variação de Temperatura (±°C)",
            min_value=0.1,
            max_value=2.0,
            value=float(config.get('simulation', 'temp_variation_range')),
            step=0.1,
            help="Variação aleatória adicionada às leituras"
        )
        
        if st.button("Salvar Configurações de Simulação", key="save_simulation"):
            config.set('simulation', 'normal_temp_evaporator_min', sim_min)
            config.set('simulation', 'normal_temp_evaporator_max', sim_max)
            config.set('simulation', 'failure_probability', failure_prob / 100)
            config.set('simulation', 'failure_duration_seconds', failure_duration)
            config.set('simulation', 'temp_variation_range', temp_variation)
            st.success("✓ Configurações de simulação salvas com sucesso!")
    
    # Aba 7: Configurações Avançadas
    with tabs[6]:
        st.subheader("🔧 Configurações Avançadas")
        
        dashboard_title = st.text_input(
            "Título do Dashboard",
            value=config.get('ui_settings', 'dashboard_title'),
            help="Título personalizado para o dashboard"
        )
        
        show_advanced = st.checkbox(
            "Mostrar Métricas Avançadas",
            value=config.get('ui_settings', 'show_advanced_metrics'),
            help="Exibir métricas e estatísticas adicionais"
        )
        
        if st.button("Salvar Configurações Avançadas", key="save_advanced"):
            config.set('ui_settings', 'dashboard_title', dashboard_title)
            config.set('ui_settings', 'show_advanced_metrics', show_advanced)
            st.success("✓ Configurações avançadas salvas com sucesso!")
        
        st.markdown("---")
        st.markdown("**Gerenciamento de Configuração**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Redefinir para Padrões", key="reset_config"):
                if st.checkbox("Confirmar redefinição para configuração padrão", key="confirm_reset"):
                    config.reset_to_default()
                    st.success("✓ Configuração redefinida para padrões!")
                    st.rerun()
        
        with col2:
            if st.button("Exportar Configuração", key="export_config"):
                export_path = f"freezer_config_backup_{datetime.now(ZoneInfo("America/Sao_Paulo"))
.strftime('%Y%m%d_%H%M%S')}.json"
                if config.export_config(export_path):
                    st.success(f"✓ Configuração exportada para {export_path}")
        
        with col3:
            st.download_button(
                "Baixar Arquivo de Config",
                data=open('freezer_config.json', 'r').read() if os.path.exists('freezer_config.json') else "",
                file_name=f"freezer_config_{datetime.now(ZoneInfo("America/Sao_Paulo"))
.strftime('%Y%m%d')}.json",
                mime="application/json",
                disabled=not os.path.exists('freezer_config.json')
            )
