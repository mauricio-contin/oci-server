import discord
from discord.ext import commands
import oci
import schedule
import threading
import time
from datetime import datetime, timedelta

# Configuração do Discord
TOKEN = 'TOKEN_DISCORD'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configuração da OCI
config = oci.config.from_file("~/.oci/config", "DEFAULT")  # Ajuste o caminho, se necessário
compute_client = oci.core.ComputeClient(config)

# ID da instância na OCI
INSTANCE_ID = "OCID_INSTANCIA"
shutdown_delay = 0  # Em horas, 0 significa sem adiamento
shutdown_time_weekdays = "05:00"  # Horário de desligamento de segunda a sexta
shutdown_time_weekend = "06:00"  # Horário de desligamento no sábado e domingo

# Variável para armazenar o próximo horário de desligamento
next_shutdown_time = None

# Funções para gerenciar a instância
def start_instance():
    response = compute_client.instance_action(INSTANCE_ID, "START")
    return response.data.lifecycle_state

def stop_instance():
    response = compute_client.instance_action(INSTANCE_ID, "STOP")
    return response.data.lifecycle_state

# Atualiza o próximo horário de desligamento com base nos horários configurados
def update_shutdown_time():
    global next_shutdown_time
    now = datetime.now()

    # Define o horário de desligamento dependendo do dia da semana
    if now.weekday() < 5:  # Dias úteis (segunda a sexta)
        shutdown_time = f"{now.date()} {shutdown_time_weekdays}"
    else:  # Fim de semana (sábado e domingo)
        shutdown_time = f"{now.date()} {shutdown_time_weekend}"

    next_shutdown_time = datetime.strptime(shutdown_time, "%Y-%m-%d %H:%M")
    if next_shutdown_time <= now:
        # Se o horário já passou hoje, configura para o próximo dia
        next_shutdown_time += timedelta(days=1)

# Calcula o tempo restante até o próximo desligamento
def calculate_time_remaining():
    if next_shutdown_time:
        remaining_time = next_shutdown_time - datetime.now()
        if remaining_time.total_seconds() > 0:
            return str(remaining_time).split(".")[0]
    return "Sem desligamentos programados."

# Função agendada para desligar a instância
def scheduled_stop():
    global shutdown_delay
    if shutdown_delay > 0:
        shutdown_delay -= 1  # Reduz o adiamento a cada hora
    else:
        try:
            stop_instance()
            print(f"[{datetime.now()}] Instância foi parada automaticamente.")
            update_shutdown_time()  # Atualiza o próximo desligamento
        except Exception as e:
            print(f"Erro ao tentar parar a instância: {e}")

# Função para rodar tarefas agendadas
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Configura os agendamentos iniciais
def configure_schedule():
    schedule.clear()
    schedule.every().day.at(shutdown_time_weekdays).do(scheduled_stop)
    schedule.every().saturday.at(shutdown_time_weekend).do(scheduled_stop)
    schedule.every().sunday.at(shutdown_time_weekend).do(scheduled_stop)
    update_shutdown_time()

configure_schedule()

# Thread para executar o schedule
threading.Thread(target=run_schedule, daemon=True).start()

# Comandos do bot
@bot.command(name="iniciar")
async def iniciar(ctx):
    try:
        status = start_instance()
        await ctx.send(f"Instância está iniciando. Status atual: {status}.")
    except Exception as e:
        await ctx.send(f"Erro ao iniciar a instância: {e}")

@bot.command(name="parar")
async def parar(ctx):
    try:
        status = stop_instance()
        await ctx.send(f"Instância está parando. Status atual: {status}.")
    except Exception as e:
        await ctx.send(f"Erro ao parar a instância: {e}")

@bot.command(name="status")
async def verificar_status(ctx):
    try:
        response = compute_client.get_instance(INSTANCE_ID)
        await ctx.send(f"Status atual da instância: {response.data.lifecycle_state}.")
    except Exception as e:
        await ctx.send(f"Erro ao obter o status da instância: {e}")

@bot.command(name="adiar")
async def adiar(ctx, horas: int):
    """Adia o desligamento da instância em X horas."""
    global shutdown_delay
    if horas > 0:
        shutdown_delay += horas
        await ctx.send(f"O desligamento automático foi adiado em {horas} horas.")
    else:
        await ctx.send("Por favor, insira um número de horas válido.")

@bot.command(name="tempo_restante")
async def tempo_restante(ctx):
    """Consulta o tempo restante até o próximo desligamento."""
    time_left = calculate_time_remaining()
    await ctx.send(f"Tempo restante até o próximo desligamento: {time_left}.")

@bot.command(name="alterar_horario")
async def alterar_horario(ctx, dia: str, horario: str):
    """Altera o horário de desligamento para dias úteis ou fins de semana."""
    global shutdown_time_weekdays, shutdown_time_weekend
    if dia.lower() in ['semana', 'dias_uteis']:
        shutdown_time_weekdays = horario
        await ctx.send(f"Novo horário de desligamento para dias úteis: {horario}.")
    elif dia.lower() in ['fim_de_semana', 'sabado', 'domingo']:
        shutdown_time_weekend = horario
        await ctx.send(f"Novo horário de desligamento para fins de semana: {horario}.")
    else:
        await ctx.send("Dia inválido! Use 'semana' ou 'fim_de_semana'.")
    configure_schedule()  # Reconfigura os agendamentos com os novos horários

@bot.event
async def on_voice_state_update(member, before, after):
    """
    Monitora mudanças de estado de voz e inicia o servidor
    automaticamente quando um usuário específico entra no canal "Satiscord".
    """
    try:
        # Verifica se o usuário entrou em um canal de voz
        if before.channel != after.channel and after.channel:
            # Nome ou IDs dos usuários-alvo
            target_users = ["mitshow", "maucontin"]
            target_channel = "Satiscord"  # Nome do canal específico
            
            # Se o nome do canal corresponder e o usuário for um dos alvos
            if after.channel.name == target_channel and member.name in target_users:
                # Inicia o servidor
                status = start_instance()
                print(f"Usuário {member.name} entrou no canal {target_channel}. Servidor iniciado.")
                # Envia mensagem de confirmação no canal de texto padrão do servidor
                default_channel = discord.utils.get(member.guild.text_channels, name="geral")  # Ajuste conforme o canal desejado
                if default_channel:
                    await default_channel.send(f"Usuário {member.name} entrou no canal {target_channel}. O servidor está iniciando. Status atual: {status}.")
    except Exception as e:
        print(f"Erro ao processar entrada no canal de voz: {e}")


# Inicializa o bot
bot.run(TOKEN)
