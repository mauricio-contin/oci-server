import discord
import oci
import asyncio
import schedule
import time
from datetime import datetime

# Configurações do bot
TOKEN = 'MTMwNDU5MTA0NTc2OTgyMjI1OQ.G8VRFB.I23CPHkeKt-v4oM8ESUKko_stWNg25-uacAj6A'  # Substitua pelo seu token de bot
INSTANCE_OCID = 'ocid1.instance.oc1.sa-saopaulo-1.antxeljr6sqfzdiclm44tndv553t47jv5enxvceyc7ihegd2hsmpkuzaxirq'  # Substitua pelo OCID da sua instância

# Cliente OCI
config = oci.config.from_file()  # Usa o arquivo de configuração padrão
compute_client = oci.core.ComputeClient(config)

# Criação do cliente Discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Funções para iniciar e parar a instância
async def start_instance():
    try:
        compute_client.instance_action(INSTANCE_OCID, 'START')
        return "Instância iniciada com sucesso!"
    except Exception as e:
        return f"Erro ao iniciar a instância: {str(e)}"

async def stop_instance():
    try:
        compute_client.instance_action(INSTANCE_OCID, 'STOP')
        return "Instância parada com sucesso!"
    except Exception as e:
        return f"Erro ao parar a instância: {str(e)}"


# Função para agendar a parada da instância
def schedule_stop_task():
    # Agendando o comando para rodar todos os dias às 05:00
    schedule.every().day.at("05:00").do(stop_instance_task)

def stop_instance_task():
    # Tarefa que executa o comando de parada
    print("Executando o comando !stop...")
    asyncio.run(stop_instance())

# Comandos do bot
@client.event
async def on_ready():
    print(f'Bot logado como {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignorar mensagens enviadas pelo próprio bot

    if message.content.lower() == '!start':
        response = await start_instance()
        await message.channel.send(response)

    elif message.content.lower() == '!stop':
        response = await stop_instance()
        await message.channel.send(response)

 # Laço para verificar as tarefas agendadas a cada 1 segundo
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar o bot
client.run(TOKEN)
