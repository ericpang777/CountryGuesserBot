import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = discord.ext.commands.Bot(command_prefix="!")

@bot.command(name="test")
async def on_message(ctx):
    await ctx.send("Hi")

bot.run(TOKEN)