import discord
from discord.ext import commands
import asyncio
import re
from collections import defaultdict
from datetime import datetime

TOKEN = 'SEU_TOKEN_AQUI'

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="s!", intents=intents)

# moderação
blacklist = ["doente mental", "cadela", "retardado", "viado", "podre", "asqueroso", "nojento", "imprestável", "ridículo",
             "patético", "traidor", "hipócrita", "imundo", "cretino", "estúpido", "burro", "imbecil", "idiota", "babaca",
             "otário", "trouxa", "escroto", "lixo", "miserável", "vagabunda", "piranha", "puto", "arrombado", "fuder",
             "foda-se", "desgraça", "bosta", "porra", "caralho", "puta", "merda"]

# Lista de palavras bloqueadas para banimento
ban_blacklist = ["débil mental", "bichona", "homossexualzinho", "boiola", "baitola", "veadinho", "transviado", "travesti",
                 "esquizofrênico", "aleijadinho", "fascista", "nazista", "judeu safado", "crioulo", "demente", "macaco",
                 "sapatão", "aleijado", "traveco"]

# Substitua pelos IDs dos cargos que deseja ignorar
role_ids_to_ignore = [1241098343317508156,1241104535905243177,1241085515202297866]

# Defina o número máximo de caracteres em maiúsculas permitidos antes de considerar como spam de capslock
CAPS_THRESHOLD = 6

# Defina o número máximo de mensagens permitidas em um intervalo de tempo
SPAM_THRESHOLD = 5  # Por exemplo, 5 mensagens em 10 segundos

# Intervalo de tempo em que as mensagens serão monitoradas para detectar spam (em segundos)
SPAM_INTERVAL = 5

# Dicionário para rastrear quantas mensagens cada usuário enviou recentemente
spam_tracker = defaultdict(lambda: defaultdict(int))

# ID do canal onde deseja registrar os avisos
log_channel_id = 1242863871258267778  # Substitua pelo ID do seu canal de log

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user.name}")
    log_channel = bot.get_channel(log_channel_id)
    if log_channel:
        print(f"Canal de log encontrado: {log_channel.name}")
    else:
        print("Canal de log não encontrado")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Verifica se o autor da mensagem possui permissões de administrador
    if message.author.guild_permissions.administrator:
        return
    
    # Verifica se o autor da mensagem possui algum dos cargos ignorados
    if any(role.id in role_ids_to_ignore for role in message.author.roles):
        return
    
    content = message.content
    words = content.split()

    # Verifica se mais de CAPS_THRESHOLD caracteres são maiúsculos
    for word in words:

        if len(re.findall(r'[A-Z]', word)) > CAPS_THRESHOLD:
            await message.delete()

            embed = discord.Embed(
                title="Aviso de Moderação ⚠️",
                description="Detectamos o uso excessivo de letras maiúsculas em uma palavra. Por favor, evite usar capslock em excesso para manter a conversa legível e agradável para todos.",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Sistema de Moderação")
            
            await message.author.send(embed=embed)
            
            # Log do aviso de capslock
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="Aviso de Moderação",
                    description=f"Usuário: {message.author.mention}\n"
                                f"Motivo: Uso excessivo de capslock\n"
                                f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x000000
                )
                log_embed.set_footer(text="Registro Automático")
                await log_channel.send(embed=log_embed)
            else:
                print("Não foi possível encontrar o canal de log")
            print(f"Mensagem deletada por capslock: {message.content}")

            break


    if any(word in message.content.lower() for word in blacklist):
        # Exclui a mensagem
        await message.delete()

        # Cria uma embed
        embed = discord.Embed(
            title="Aviso de Moderação  ⚠️",
            description="Detectamos o uso de uma palavra inadequada. Por favor, mantenha a conversa respeitosa.\n"
                        "Se algo aconteceu fora das [regras](https://discord.com/channels/1241052393165160508/1241173127552303104), "
                        "abra um ticket para falar com um administrador.",
            color=0xFFFF00
        )
        embed.set_footer(text="Sistema de Moderação")
        
        # Envia a embed como uma mensagem privada
        await message.author.send(embed=embed)

        # Log da mensagem moderada
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="Aviso de Moderação",
                description=f"Usuário: {message.author.mention}\n"
                            f"Palavra Bloqueada: {word}\n"
                            f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                color=0x000000
            )
            log_embed.set_footer(text="Registro Automático")
            await log_channel.send(embed=log_embed)
        else:
            print("Não foi possível encontrar o canal de log")
        print(f"Mensagem deletada por palavra bloqueada: {message.content}")

    if any(word in message.content.lower() for word in ban_blacklist):
        # Exclui a mensagem
        await message.delete()
        
        # Banir o usuário
        await message.guild.ban(message.author, reason="Uso de Linguagem discriminatória")
        
        # Cria uma embed de banimento
        embed = discord.Embed(
            title="⚠️ BANIMENTO ⚠️",
            description="Linguagem discriminatória não será tolerada. Você foi permanentemente banido do servidor. Suas ações violaram nossas diretrizes.",
            color=0xFF0000
        )
        embed.set_footer(text="Sistema de Moderação")
        
        # Envia a embed como uma mensagem privada
        await message.author.send(embed=embed)

        # Log do banimento
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="Aviso de Banimento",
                description=f"Usuário Banido: {message.author.mention}\n"
                            f"Motivo: Uso de linguagem discriminatória\n"
                            f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                color=0x000000
            )
            log_embed.set_footer(text="Registro Automático")
            await log_channel.send(embed=log_embed)
        else:
            print("Não foi possível encontrar o canal de log")
        print(f"Mensagem deletada por palavra bloqueada: {message.content}")

    # Verificação de spam de mensagens
    spam_tracker[message.author.id]['message_count'] += 1

    # Limpa o rastreador de spam após o intervalo de tempo especificado
    await asyncio.sleep(SPAM_INTERVAL)
    spam_tracker[message.author.id]['message_count'] = max(0, spam_tracker[message.author.id]['message_count'] - 1)

    # Verifica se o usuário excedeu o limite de spam
    if spam_tracker[message.author.id]['message_count'] > SPAM_THRESHOLD:
              # Obtém as mensagens do usuário no canal onde ocorreu o spam
        user_messages = []
        async for msg in message.channel.history(limit=spam_tracker[message.author.id]['message_count']):
            if msg.author == message.author:
                user_messages.append(msg)

        # Exclui todas as mensagens do usuário
        for msg in user_messages:
            await msg.delete()

        # Cria uma embed de aviso por spam
        embed = discord.Embed(
            title="Aviso de Moderação  ⚠️",
            description="Você está enviando mensagens muito rapidamente. Por favor, evite spam para manter a conversa organizada.",
            color=0xFFFF00
        )
        embed.set_footer(text="Sistema de Moderação")
        
        # Envia a embed como uma mensagem privada
        await message.author.send(embed=embed)

        # Log do spam
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            log_embed = discord.Embed(
                title="Aviso de Moderação",
                description=f"Usuário: {message.author.mention}\n"
                            f"Motivo: Spam de mensagens\n"
                            f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                color=0x000000
            )
            log_embed.set_footer(text="Registro Automático")
            await log_channel.send(embed=log_embed)
        else:
            print("Não foi possível encontrar o canal de log")
        print(f"Mensagens deletadas por spam: {message.author.name}")

    await bot.process_commands(message)

bot.run(TOKEN)