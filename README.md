# Bot Discord para Controle de Servidor OCI

Este projeto implementa um bot do Discord que permite ligar e desligar servidores na **Oracle Cloud Infrastructure (OCI)** usando comandos no Discord.

## Funcionalidades
- `!ligar`: Inicia o servidor configurado na OCI.
- `!desligar`: Desliga o servidor configurado na OCI.
- `!status`: Verifica o status atual da instância.
- `!adiar <horas>`: Adia o desligamento automático em um número específico de horas.
- `!tempo_restante`: Consulta quanto tempo falta para o próximo desligamento.
- `!alterar_horario` <semana/fim_de_semana> <horário>: Altera os horários de desligamento para dias úteis ou finais de semana.

## Pré-requisitos
1. Um bot do Discord configurado ([guia aqui](https://discord.com/developers/applications)).
2. Acesso à OCI com:
   - OCID do usuário.
   - OCID do tenant.
   - OCID da instância.
   - Chaves configuradas.
3. Servidor Linux com Python 3.10+ e acesso à internet.

## Instalação
### 1. Clone o repositório
```bash
git clone (https://github.com/mauricio-contin/oci-server.git)
cd bot-oci
