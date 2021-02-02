import discord
from discord.ext import commands, tasks
import secret
from random import randint, choice
import youtube_dl
import os
from datetime import datetime

hello_list = ['Hello, {}! How are you?', 'Heeey, {}! How are you doing?', "What's up, {}?     :)", 'Hi there, {}!',
              'Yooo! Sup, {}?', 'Hi, {}! How is it going?', 'Hey, {} from across the street. Lemme hold a dollar.',
              'Hey, {}. Nice to see you!       :D', 'Howdy, {}!']

status = ['Eating bacon.', 'I lost The Game!', 'Flying Spaghetti Monster is real!', '!help']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as: {0.user}'.format(bot))
    await change_status.start()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')

    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have the required permission to use this command.")


@bot.command(help='Return the name of my creator.')
async def credits(ctx):
    await ctx.send(f'Made by `Dizzy#9551`.')


@bot.command()
async def help(ctx):
    embed = discord.Embed(colour=discord.Color.orange())

    embed.set_author(name='Help')
    embed.add_field(name='!clear', value='Delete the last 10 messages. You can specify how many messages you want '
                                         'delete. For example: !clear 5', inline=False)
    embed.add_field(name='!credits', value='Return the name of my creator.', inline=False)
    embed.add_field(name='!help', value='Show all the commands.', inline=False)
    embed.add_field(name='!hello', value='Say types of hello.', inline=False)
    embed.add_field(name='!server', value='Return the name of the server.', inline=False)
    embed.add_field(name='!join or !j', value='Join a voice channel.', inline=False)
    embed.add_field(name='!leave or !l', value='Leave a voice channel.', inline=False)
    embed.add_field(name='!play or !p', value='Join a voice channel and play the url. To search on youtube, '
                                        'use !play ytsearch:YOUR SEARCH HERE', inline=False)
    embed.add_field(name='!pause', value='Pause the music that is currently playing.', inline=False)
    embed.add_field(name='!resume', value='Resume the music that is paused.', inline=False)
    embed.add_field(name='!stop', value='Stop playing the music.', inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def hello(ctx):
    """
    Say types of hello.
    :param ctx: Context
    """

    await ctx.channel.send(hello_list[randint(0, len(hello_list) - 1)].format(ctx.author.name))


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def server(ctx):
    icon = str(ctx.guild.icon_url)
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)
    owner = str(ctx.guild.owner)
    region = str(ctx.guild.region)
    member_count = str(ctx.guild.member_count)
    roles = str(ctx.guild.roles)
    voice_channel = str(ctx.guild.voice_channels)
    text_channel = str(ctx.guild.text_channels)
    date = datetime.now()

    embed = discord.Embed(colour=discord.Color.blue(), title=name)
    embed.set_thumbnail(url=icon)
    embed.add_field(name='Owner:', value=f'`{owner}`', inline=False)
    embed.add_field(name='Region:', value=f'`{region.capitalize()}`', inline=False)
    embed.add_field(name='Members:', value=f'`{member_count}`', inline=False)
    embed.add_field(name='Roles:', value=f'`{roles.count("Role") - 5}`', inline=False)
    embed.add_field(name='Text Channels:', value=f'`{text_channel.count("TextChannel")}`', inline=False)
    embed.add_field(name='Voice Channels:', value=f'`{voice_channel.count("VoiceChannel")}`', inline=False)
    embed.set_footer(text=str(date.strftime('%d %b %Y - %H:%M:%S')))

    await ctx.send(embed=embed)


@bot.command(aliases=['j'])
async def join(ctx):
    """
    Join a voice channel.
    :param ctx: Context
    """

    try:
        connected = ctx.author.voice
        if connected:
            await connected.channel.connect()
        else:
            await ctx.channel.send('You need to be connected on a voice channel.')
    except discord.errors.ClientException:
        await leave(ctx)
        connected = ctx.author.voice
        await connected.channel.connect()


@bot.command(aliases=['l'])
async def leave(ctx):
    """
    Leave a voice channel.
    :param ctx: Context
    """

    try:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        await voice.disconnect()
    except:
        pass


@bot.command(aliases=['p'])
async def play(ctx, url: str):
    """
    Join a voice channel and play the url.
    To search on youtube, use !play ytsearch:YOUR SEARCH HERE
    :param ctx: Context
    :param url: Youtube URL
    """

    await join(ctx)

    song = os.path.isfile('song.mp3')

    try:
        if song:
            os.remove('song.mp3')
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command.")
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir('./'):
        if file.endswith('.mp3'):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio('song.mp3'))


@bot.command()
async def pause(ctx):
    """
    Pause the music that is currently playing.
    :param ctx: Context
    """

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('There is nothing playing at the moment.')


@bot.command()
async def resume(ctx):
    """
    Resume the music that is paused.
    :param ctx: Context
    """

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('Nothing to unpause here.')


@bot.command()
async def stop(ctx):
    """
    Stop playing the music.
    :param ctx: Context
    """

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@tasks.loop(seconds=30)
async def change_status():
    await bot.change_presence(activity=discord.Game(choice(status)))


bot.run(secret.token)
