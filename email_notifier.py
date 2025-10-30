"""
Email Notification Module
Handles automated email alerts for critical temperature events
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from typing import Dict, List
from config_manager import ConfigManager

class EmailNotifier:
    """Manages email notifications for temperature alerts"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the email notifier
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.last_alert_time = {}
        self.consecutive_critical_count = {}
    
    def _get_smtp_password(self) -> str:
        """
        Get SMTP password from environment variable
        
        Returns:
            SMTP password from environment or empty string
        """
        import os
        return os.environ.get('SMTP_PASSWORD', '')
    
    def _is_configured(self) -> bool:
        """
        Check if email configuration is complete
        
        Returns:
            True if configured, False otherwise
        """
        sender_email = self.config.get('email_config', 'sender_email')
        sender_password = self._get_smtp_password()
        recipients = self.config.get('email_config', 'recipient_emails')
        
        return (sender_email and sender_password and recipients and len(recipients) > 0)
    
    def _can_send_alert(self, alert_key: str) -> bool:
        """
        Check if enough time has passed since last alert (cooldown)
        
        Args:
            alert_key: Unique key for this type of alert
            
        Returns:
            True if alert can be sent, False if in cooldown period
        """
        if not self.config.get('alert_settings', 'enable_email_alerts'):
            return False
        
        cooldown_seconds = self.config.get('alert_settings', 'alert_cooldown_seconds')
        
        if alert_key not in self.last_alert_time:
            return True
        
        time_since_last = datetime.now(ZoneInfo("America/Sao_Paulo")) - self.last_alert_time[alert_key]
        return time_since_last.total_seconds() >= cooldown_seconds
    
    def _update_consecutive_count(self, zone: str, is_critical: bool):
        """
        Update consecutive critical reading count for a zone
        
        Args:
            zone: Temperature zone name
            is_critical: Whether current reading is critical
        """
        if is_critical:
            self.consecutive_critical_count[zone] = self.consecutive_critical_count.get(zone, 0) + 1
        else:
            self.consecutive_critical_count[zone] = 0
    
    def _should_trigger_alert(self, zone: str) -> bool:
        """
        Check if alert should be triggered based on consecutive readings
        
        Args:
            zone: Temperature zone name
            
        Returns:
            True if alert should be triggered
        """
        required_count = self.config.get('alert_settings', 'consecutive_readings_trigger')
        current_count = self.consecutive_critical_count.get(zone, 0)
        return current_count >= required_count
    
    def _create_alert_email(self, reading: Dict, status: Dict) -> MIMEMultipart:
        """
        Create email message for temperature alert
        
        Args:
            reading: Temperature reading data
            status: Status information for all zones
            
        Returns:
            Email message object
        """
        msg = MIMEMultipart('alternative')
        
        # Email subject
        freezer_model = self.config.get('freezer_info', 'model_name')
        msg['Subject'] = f"🚨 ALERTA CRÍTICO: {freezer_model} - Limite de Temperatura Excedido"
        msg['From'] = self.config.get('email_config', 'sender_email')
        msg['To'] = ', '.join(self.config.get('email_config', 'recipient_emails'))
        
        # Create email body
        critical_zones = [zone for zone, stat in status.items() if stat == 'CRITICAL' and zone != 'overall']
        
        # Plain text version
        text_body = f"""
ALERTA DE TEMPERATURA CRÍTICA
{'=' * 50}

Informações do Freezer:
- Modelo: {self.config.get('freezer_info', 'model_name')}
- Localização: {self.config.get('freezer_info', 'location')}
- Horário: {reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

ZONAS CRÍTICAS: {', '.join(critical_zones).upper()}

Leituras Atuais:
- Evaporador: {reading['evaporator_temp']:.2f}°C [{status['evaporator']}]
- Condensador: {reading['condenser_temp']:.2f}°C [{status['condenser']}]
- Ambiente: {reading['ambient_temp']:.2f}°C [{status['ambient']}]

Limites de Temperatura:
"""
        
        # Add threshold information for critical zones
        zone_names = {'evaporator': 'Evaporador', 'condenser': 'Condensador', 'ambient': 'Ambiente'}
        for zone in critical_zones:
            thresholds = self.config.get('temperature_thresholds', zone)
            text_body += f"\n{zone_names.get(zone, zone.capitalize())}:\n"
            text_body += f"  - Faixa Normal: {thresholds['min']:.1f}°C a {thresholds['max']:.1f}°C\n"
            text_body += f"  - Limites Críticos: {thresholds['critical_low']:.1f}°C a {thresholds['critical_high']:.1f}°C\n"
        
        text_body += f"""
{'=' * 50}

AÇÃO IMEDIATA NECESSÁRIA!

Contato: {self.config.get('freezer_info', 'operator_name')}
E-mail: {self.config.get('freezer_info', 'operator_contact')}

Este é um alerta automático do Sistema de Monitoramento de Freezer FAST BOMBAS.
"""
        
        # HTML version
        zone_names = {'evaporator': 'Evaporador', 'condenser': 'Condensador', 'ambient': 'Ambiente'}
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #ddd; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-weight: bold; color: #dc3545; margin-bottom: 10px; }}
        .reading {{ background-color: white; padding: 10px; margin: 5px 0; border-left: 4px solid #dc3545; }}
        .reading.ok {{ border-left-color: #28a745; }}
        .reading.warning {{ border-left-color: #ffc107; }}
        .reading.critical {{ border-left-color: #dc3545; }}
        .footer {{ background-color: #343a40; color: white; padding: 15px; text-align: center; border-radius: 0 0 5px 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        td {{ padding: 8px; }}
        .label {{ font-weight: bold; width: 40%; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 ALERTA DE TEMPERATURA CRÍTICA</h1>
            <p>Ação Imediata Necessária</p>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">Informações do Freezer</div>
                <table>
                    <tr><td class="label">Modelo:</td><td>{self.config.get('freezer_info', 'model_name')}</td></tr>
                    <tr><td class="label">Localização:</td><td>{self.config.get('freezer_info', 'location')}</td></tr>
                    <tr><td class="label">Horário do Alerta:</td><td>{reading['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                    <tr><td class="label">Zonas Críticas:</td><td style="color: #dc3545; font-weight: bold;">{', '.join([zone_names.get(z, z.upper()) for z in critical_zones])}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">Leituras de Temperatura Atuais</div>
                <div class="reading {status['evaporator'].lower()}">
                    <strong>Evaporador:</strong> {reading['evaporator_temp']:.2f}°C 
                    <span style="float: right; font-weight: bold;">[{status['evaporator']}]</span>
                </div>
                <div class="reading {status['condenser'].lower()}">
                    <strong>Condensador:</strong> {reading['condenser_temp']:.2f}°C 
                    <span style="float: right; font-weight: bold;">[{status['condenser']}]</span>
                </div>
                <div class="reading {status['ambient'].lower()}">
                    <strong>Ambiente:</strong> {reading['ambient_temp']:.2f}°C 
                    <span style="float: right; font-weight: bold;">[{status['ambient']}]</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Limites de Temperatura</div>
"""
        
        for zone in critical_zones:
            thresholds = self.config.get('temperature_thresholds', zone)
            html_body += f"""
                <p><strong>{zone_names.get(zone, zone.capitalize())}:</strong><br>
                Faixa Normal: {thresholds['min']:.1f}°C a {thresholds['max']:.1f}°C<br>
                Limites Críticos: {thresholds['critical_low']:.1f}°C a {thresholds['critical_high']:.1f}°C</p>
"""
        
        html_body += f"""
            </div>
            
            <div class="section" style="background-color: #fff3cd; padding: 15px; border: 1px solid #ffc107;">
                <strong>⚠️ AÇÃO IMEDIATA NECESSÁRIA!</strong><br>
                Contato: {self.config.get('freezer_info', 'operator_name')}<br>
                E-mail: {self.config.get('freezer_info', 'operator_contact')}
            </div>
        </div>
        
        <div class="footer">
            <p>Este é um alerta automático do Sistema de Monitoramento de Freezer FAST BOMBAS</p>
            <p style="font-size: 12px; margin-top: 10px;">Não responda a este e-mail</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        return msg
    
    def send_alert(self, reading: Dict, status: Dict) -> bool:
        """
        Send email alert for critical temperature condition
        
        Args:
            reading: Temperature reading data
            status: Status information for all zones
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Check if email is configured
        if not self._is_configured():
            print("Email not configured. Skipping alert.")
            return False
        
        # Update consecutive counts
        for zone in ['evaporator', 'condenser', 'ambient']:
            is_critical = status[zone] == 'CRITICAL'
            self._update_consecutive_count(zone, is_critical)
        
        # Check if we should trigger alert based on consecutive readings
        critical_zones = [zone for zone in ['evaporator', 'condenser', 'ambient'] 
                         if self._should_trigger_alert(zone)]
        
        if not critical_zones:
            return False
        
        # Check cooldown for overall critical status
        alert_key = 'critical_temp_alert'
        if not self._can_send_alert(alert_key):
            return False
        
        try:
            # Create email message
            msg = self._create_alert_email(reading, status)
            
            # Connect to SMTP server
            smtp_server = self.config.get('email_config', 'smtp_server')
            smtp_port = self.config.get('email_config', 'smtp_port')
            use_tls = self.config.get('email_config', 'use_tls')
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            
            if use_tls:
                server.starttls()
            
            # Login
            sender_email = self.config.get('email_config', 'sender_email')
            sender_password = self._get_smtp_password()
            server.login(sender_email, sender_password)
            
            # Send email
            recipients = self.config.get('email_config', 'recipient_emails')
            server.send_message(msg)
            server.quit()
            
            # Update last alert time
            self.last_alert_time[alert_key] = datetime.now(ZoneInfo("America/Sao_Paulo"))
            
            print(f"E-mail de alerta enviado com sucesso para {len(recipients)} destinatário(s)")
            return True
            
        except Exception as e:
            print(f"Falha ao enviar e-mail de alerta: {e}")
            return False
    
    def test_email_connection(self) -> tuple[bool, str]:
        """
        Test email configuration and connection
        
        Returns:
            Tuple of (success, message)
        """
        if not self._is_configured():
            return False, "Configuração de e-mail incompleta. Por favor, configure o e-mail remetente, senha e destinatários."
        
        try:
            smtp_server = self.config.get('email_config', 'smtp_server')
            smtp_port = self.config.get('email_config', 'smtp_port')
            use_tls = self.config.get('email_config', 'use_tls')
            
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            
            if use_tls:
                server.starttls()
            
            sender_email = self.config.get('email_config', 'sender_email')
            sender_password = self._get_smtp_password()
            server.login(sender_email, sender_password)
            server.quit()
            
            return True, "Conexão de e-mail bem-sucedida!"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Falha na autenticação. Por favor, verifique seu e-mail e senha."
        except smtplib.SMTPException as e:
            return False, f"Erro SMTP: {str(e)}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"
