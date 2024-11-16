# oci-server

Para transformar a criação do seu **Discord Bot** que interage com instâncias da **OCI (Oracle Cloud Infrastructure)** em um repositório no **GitHub**, você precisará organizar o código de forma modular e documentada. Vou te guiar pelos passos necessários para criar um repositório GitHub que inclui:

1. O código do bot do Discord.
2. O agendamento da parada e início da instância na OCI.
3. Dependências necessárias e instruções para configurar e rodar o bot.

### Estrutura do Projeto

Aqui está a estrutura do projeto que vamos criar:

```
discord-oci-bot/
│
├── bot.py                     # Código principal do bot
├── requirements.txt            # Dependências do Python
├── config.ini                  # Arquivo de configuração (OCID, Token do Discord, etc.)
├── Procfile                    # Para rodar no Heroku (se necessário)
└── README.md                   # Instruções para rodar o bot
```

### Passo 1: Criar o Código do Bot

1. **Criação do arquivo `bot.py`**:

   O `bot.py` será o código principal do bot que interage com o Discord e com a OCI. Aqui está um exemplo de como o bot pode ser configurado para iniciar e parar instâncias na OCI com comandos do Discord:

```python
import discord
import oci
import asyncio
import schedule
import time
from datetime import datetime
import configparser

# Carregar configurações do arquivo .ini
config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['discord']['TOKEN']
INSTANCE_OCID = config['oci']['INSTANCE_OCID']
CHANNEL_ID = int(config['discord']['CHANNEL_ID'])

# Cliente OCI
oci_config = oci.config.from_file()  # Leitura da configuração do OCI (config.ini)
compute_client = oci.core.ComputeClient(oci_config)

# Configuração do cliente do Discord
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Função para iniciar e parar a instância na OCI
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

# Função para enviar comandos no Discord
async def send_command_to_channel(command):
    channel = client.get_channel(CHANNEL_ID)  # Canal para enviar a mensagem
    if channel:
        await channel.send(command)
    else:
        print("Canal não encontrado!")

# Função de agendamento da parada da instância
def schedule_stop_task():
    schedule.every().day.at("05:00").do(stop_instance_task)

def stop_instance_task():
    print("Executando o comando para parar a instância...")
    asyncio.run(stop_instance())
    asyncio.run(send_command_to_channel("!stop"))  # Envia o comando !stop no Discord

# Evento chamado quando o bot estiver pronto
@client.event
async def on_ready():
    print(f'Bot logado como {client.user}')
    schedule_stop_task()  # Agendar a parada da instância
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar o bot
client.run(TOKEN)
```

**O que está acontecendo no código?**

- O bot do Discord lê o token e o canal do Discord a partir de um arquivo de configuração (`config.ini`).
- O bot tem duas funções principais para interagir com a instância OCI: `start_instance()` e `stop_instance()`.
- Usamos o agendador `schedule` para garantir que o comando de parada da instância seja executado todos os dias às 5:00 AM.
- O bot também envia um comando `!stop` no canal do Discord, o que pode ser usado para parar ou iniciar a instância no servidor.

---

### Passo 2: Arquivo de Dependências (`requirements.txt`)

Crie o arquivo `requirements.txt` para listar todas as bibliotecas que seu bot vai precisar.

**Conteúdo do `requirements.txt`:**
```
discord.py
oci
schedule
```

Essas bibliotecas são necessárias para:
- **`discord.py`**: Conectar-se ao Discord e interagir com a API.
- **`oci`**: Interagir com a Oracle Cloud Infrastructure.
- **`schedule`**: Agendar tarefas, como desligar o servidor em horários específicos.

---

### Passo 3: Arquivo de Configuração (`config.ini`)

O arquivo `config.ini` deve armazenar informações sensíveis, como o token do Discord e o OCID da instância OCI.

**Exemplo de `config.ini`:**
```ini
[discord]
TOKEN = seu_token_do_discord
CHANNEL_ID = 123456789012345678  # ID do canal onde o bot enviará o comando !stop

[oci]
INSTANCE_OCID = ocid1.instance.oc1..xxxxxxEXAMPLExxxxxx
```

---

### Passo 4: Configuração do Heroku (opcional)

Se você decidir hospedar o bot no **Heroku**, será necessário criar um arquivo `Procfile` que define como o bot será executado.

**Conteúdo do `Procfile`:**
```
worker: python bot.py
```

---

### Passo 5: Criar o Repositório no GitHub

Agora, siga estas etapas para criar o repositório no GitHub:

1. **Criar um novo repositório** no [GitHub](https://github.com/).
   - Vá até a página inicial do GitHub.
   - Clique em "New" para criar um novo repositório.
   - Dê um nome ao repositório (por exemplo, `discord-oci-bot`) e defina-o como **público** ou **privado**.
   - Clique em "Create repository".

2. **Subir o Código para o GitHub**:
   Se você ainda não inicializou um repositório Git, faça isso dentro do diretório do projeto:

   ```bash
   git init
   git add .
   git commit -m "Adiciona o bot que interage com OCI"
   ```

   Agora, adicione o repositório remoto do GitHub:

   ```bash
   git remote add origin https://github.com/seu_usuario/discord-oci-bot.git
   git push -u origin master
   ```

3. **Verifique no GitHub**: 
   Acesse o seu repositório no GitHub para garantir que os arquivos foram enviados corretamente.

---

### Passo 6: Instruções no `README.md`

Por fim, crie um arquivo `README.md` para explicar como usar o bot. Aqui está um exemplo básico de `README.md`:

```markdown
# Discord OCI Bot

Este é um bot do Discord que interage com a Oracle Cloud Infrastructure (OCI). O bot permite iniciar e parar instâncias OCI com comandos do Discord, além de agendar a parada automática da instância todos os dias às 5:00 AM.

## Como Configurar

### 1. Clone o repositório
Clone este repositório para o seu ambiente local ou servidor:
```bash
git clone https://github.com/seu_usuario/discord-oci-bot.git
cd discord-oci-bot
```

### 2. Instale as dependências
Instale as bibliotecas necessárias usando `pip`:
```bash
pip install -r requirements.txt
```

### 3. Configuração

- Crie um arquivo `config.ini` com seu **token do Discord** e **OCID da instância OCI**.
- Exemplo de `config.ini`:
```ini
[discord]
TOKEN = seu_token_do_discord
CHANNEL_ID = 123456789012345678

[oci]
INSTANCE_OCID = ocid1.instance.oc1..xxxxxxEXAMPLExxxxxx
```

### 4. Executar o Bot

Execute o bot com o seguinte comando:
```bash
python bot.py
```

O bot ficará disponível no Discord e também irá parar e iniciar a instância OCI de acordo com o agendamento.
```

---

### Passo 7: Dicas Finais

- **Segurança**: Não compartilhe seu `config.ini` com o token do Discord ou OCID da instância. Certifique-se de adicionar o arquivo `config.ini` ao `.gitignore` para não comitar informações sensíveis.
  
- **Hospedagem**: Para garantir que o bot fique online 24/7, considere hospedá-lo em um VPS, Heroku ou outra plataforma de sua escolha.

---

### Conclusão

Com isso, você terá um bot funcional do Discord para gerenciar instâncias OCI, hospedado em um repositório GitHub com todas as dependências e configurações necessárias. Isso facilita a manutenção e a colaboração, caso queira trabalhar com outros desenvolvedores.

Se precisar de mais alguma coisa, fique à vontade para perguntar!
