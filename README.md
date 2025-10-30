# FAST BOMBAS - Sistema de Controle Térmico de Freezers

Um sistema completo de monitoramento para freezers industriais desenvolvido em Python, com acompanhamento de temperatura em tempo real, alertas automáticos e registro histórico de dados.

## Funcionalidades

- **Monitoramento em Tempo Real**: Acompanha temperaturas ao vivo em três zonas (Evaporador, Condensador e Ambiente)  
- **Painel Interativo**: Interface web profissional desenvolvida com Streamlit  
- **Indicadores Visuais**: Medidores de temperatura com indicadores de status coloridos  
- **Gráficos de Tendência**: Visualização histórica de temperatura com intervalos configuráveis  
- **Alertas Automáticos**: Notificações por e-mail em eventos de temperatura crítica  
- **Registro de Dados**: Exportação em CSV e gerenciamento de históricos  
- **Totalmente Configurável**: Todos os limites, intervalos e ajustes disponíveis na interface  
- **Modo de Simulação**: Simulador interno de temperatura para testes sem hardware real  

## Requisitos do Sistema

- Python 3.11+  
- Streamlit  
- Plotly  
- Pandas  

## Instalação

1. Todos os pacotes necessários já estão instalados neste ambiente Replit.  
2. O sistema é configurado para ser executado automaticamente pelo fluxo **Server**.  

## Configuração

### Configuração de Alertas por E-mail

Por segurança, a senha SMTP deve ser configurada como uma variável de ambiente:

- Key: `SMTP_PASSWORD`  
 - Value: sua senha SMTP ou senha de aplicativo do e-mail  

**Notas importantes de segurança:**  
- Nunca armazene senhas em arquivos de configuração  
- Utilize senhas de aplicativo sempre que possível (Gmail, Outlook, etc.)  
- O sistema só enviará alertas se a variável de ambiente `SMTP_PASSWORD` estiver definida  

### Configurando os Limites de Temperatura

1. Abra o Painel  
2. Vá até a página **Configurações**  
3. Acesse a aba **Limites de Temperatura**  
4. Configure os seguintes parâmetros para cada zona:  
   - **Normal Mín/Máx**: Faixa operacional normal  
   - **Crítico Baixo/Alto**: Limites que disparam os alertas  

### Configuração de Destinatários de E-mail

1. Vá em **Configurações** > **Alertas por E-mail**  
2. Insira os endereços de e-mail dos destinatários (um por linha)  
3. Configure as opções SMTP:  
   - Servidor SMTP (ex: `smtp.gmail.com`)  
   - Porta SMTP (geralmente 587)  
   - Endereço de e-mail do remetente  
4. Salve as configurações  

## Uso

### Visão Geral do Painel

O painel principal exibe:  
- **Status do Sistema**: Saúde geral e modo de operação  
- **Medidores de Temperatura**: Leituras em tempo real das três zonas  
- **Indicadores de Status**: Cores de status (Verde = OK, Amarelo = Aviso, Vermelho = Crítico)  
- **Tendências de Temperatura**: Gráfico histórico com as últimas 30 leituras  
- **Histórico de Alertas**: Registros recentes de avisos e eventos críticos  

### Navegação

- **Painel**: Interface principal de monitoramento  
- **Configurações**: Ajustes gerais e personalização do sistema  
- **Exportar Dados**: Exportação de históricos em CSV  
- **Informações do Sistema**: Diagnósticos e detalhes técnicos  

### Personalização de Configurações

Todas as configurações podem ser feitas na página **Configurações**:

1. **Informações do Freezer**: Modelo, localização e operador responsável  
2. **Limites de Temperatura**: Faixas mínimas, máximas e críticas por zona  
3. **Coleta de Dados**: Intervalos de leitura e atualização dos gráficos  
4. **Alertas por E-mail**: Configuração SMTP, tempo de espera e gatilhos de alerta  
5. **Registro de Dados**: Caminhos de arquivos CSV e tempo de retenção  
6. **Simulação**: Parâmetros para testes com o gerador de dados  

### Exportação de Dados

1. Acesse a página **Exportar Dados**  
2. Selecione o intervalo de tempo (horas de histórico)  
3. Clique em **Exportar para CSV**  
4. Baixe o arquivo gerado  

### Indicadores de Status

- **🟢 OK**: Temperatura dentro da faixa normal  
- **🟡 AVISO**: Temperatura fora do normal, mas ainda não crítica  
- **🔴 CRÍTICO**: Temperatura ultrapassou o limite crítico — alerta disparado!  

## Sistema de Alertas

O sistema envia alertas por e-mail quando:  
1. A temperatura ultrapassa os limites críticos  
2. Leituras críticas consecutivas são detectadas (configurável)  
3. O período de espera entre alertas já foi atingido (evita spam)  

Os e-mails de alerta incluem:  
- Data e hora do evento  
- Informações do freezer  
- Leituras atuais das três zonas  
- Indicadores de status  
- Limites configurados  
- Ações recomendadas para o operador  

## Registro de Dados

Todas as leituras de temperatura são registradas automaticamente em arquivos CSV:  
- Local padrão: `data/temperature_logs.csv`  
- Inclui: timestamp, temperaturas das zonas e status  
- Limpeza automática com base no período de retenção  
- Possibilidade de exportação por intervalos personalizados  

## Modo de Simulação

O simulador interno gera dados de temperatura realistas:  
- **Operação normal**: Oscilações dentro da faixa configurada  
- **Modo de falha**: Eventos críticos aleatórios para testar o sistema de alerta  
- **Probabilidade e duração da falha configuráveis**  
- **Transições de temperatura suaves**  

## Estrutura de Arquivos

```
├── app.py                      # Aplicação principal Streamlit
├── config_manager.py           # Gerenciamento de configurações
├── data_simulator.py           # Simulador de dados de temperatura
├── email_notifier.py           # Sistema de alertas por e-mail
├── data_logger.py              # Registro e gerenciamento de dados CSV
├── config_panel.py             # Interface de configurações
├── data_export_panel.py        # Interface de exportação de dados
├── system_info_panel.py        # Interface de informações do sistema
├── freezer_config.json         # Configuração do sistema (gerado automaticamente)
├── data/                       # Arquivos de log CSV
└── exports/                    # Arquivos exportados
```

## Boas Práticas de Segurança

1. **Nunca salve credenciais**: Senhas SMTP devem estar apenas em variáveis de ambiente  
2. **Use senhas de aplicativo**: Crie senhas específicas para alertas de e-mail  
3. **Restrinja o acesso a arquivos**: Garanta permissões adequadas nos arquivos de configuração  
4. **Mantenha o sistema atualizado**: Atualize dependências regularmente para corrigir vulnerabilidades  

## Solução de Problemas

### Alertas por E-mail Não Funcionam

1. Verifique se a variável `SMTP_PASSWORD` está definida  
2. Confirme as configurações do servidor e porta SMTP  
3. Verifique se o e-mail do remetente está correto  
4. Confira os endereços dos destinatários  
5. Utilize o botão **Testar Conexão de E-mail** em Configurações  

### Painel Não Atualiza

1. Confirme se o fluxo do servidor está ativo  
2. Verifique se o navegador não bloqueia a atualização automática  
3. Consulte o console do navegador para possíveis erros  
4. Atualize a página manualmente  

### Sem Dados Históricos

1. Verifique se o registro CSV está habilitado em Configurações  
2. Confirme se o diretório `data/` existe  
3. Garanta que há espaço suficiente em disco  
4. Verifique as permissões de arquivo  

## Suporte

Para dúvidas, problemas ou solicitações de novos recursos:  
- Contato: operator@fastbombas.com  
- Versão do Sistema: 1.0.0  

## Licença

Proprietário - FAST BOMBAS Industrial Systems  

---

**Desenvolvido para o monitoramento de freezers industriais FAST BOMBAS**
