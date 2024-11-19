import discord
from discord.ext import commands
import youtube_dl
import asyncio

# Configurações do bot
TOKEN = "SEU_TOKEN_AQUI"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Variáveis globais
queue = []
voice_client = None

# Função para tocar música
async def play_music(ctx):
    global queue, voice_client

    if not queue:
        await ctx.send("🎵 Fila de músicas vazia.")
        return

    url = queue.pop(0)
    ffmpeg_options = {'options': '-vn'}
    ydl_options = {'format': 'bestaudio/best'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']

    if voice_client and voice_client.is_connected():
        voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(url2, **ffmpeg_options), after=lambda e: asyncio.run_coroutine_threadsafe(play_music(ctx), bot.loop))
        await ctx.send(f"🎶 Tocando agora: {info['title']}")
    else:
        await ctx.send("❌ O bot não está conectado a um canal de voz.")

# Comando para se conectar a um canal de voz
@bot.command(name="join")
async def join(ctx):
    global voice_client
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f"🔊 Conectado ao canal: {channel.name}")
    else:
        await ctx.send("❌ Você precisa estar em um canal de voz.")

# Comando para adicionar música à fila
@bot.command(name="add")
async def add(ctx, url: str):
    global queue
    queue.append(url)
    await ctx.send(f"🎵 Música adicionada à fila: {url}")
    if len(queue) == 1:
        await play_music(ctx)

# Comando para pular para a próxima música
@bot.command(name="skip")
async def skip(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await play_music(ctx)
    else:
        await ctx.send("❌ Nenhuma música está tocando no momento.")

# Comando para desconectar do canal de voz
@bot.command(name="leave")
async def leave(ctx):
    global voice_client
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send("👋 Desconectado do canal de voz.")
    else:
        await ctx.send("❌ O bot não está conectado a nenhum canal de voz.")

# Evento de inicialização
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Iniciar o bot
bot.run(TOKEN)
