import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
from flask import Flask
import threading

# Initialize Flask to satisfy Render's Web Service requirement
app = Flask('')

@app.route('/')
def home():
    return "GMU Bot is active and online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Greater Manchester Utilities Bot logged in as {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="announce", description="Post an official GMU department announcement.")
@app_commands.describe(title="Announcement Title", message="Announcement content")
async def announce(interaction: discord.Interaction, title: str, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📢 GMU Official Notice: {title}",
        description=message,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="Greater Manchester Utilities | ERLC Roleplay")
    
    await interaction.response.send_message("Announcement posted successfully!", ephemeral=True)
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="links", description="Get official Greater Manchester Utilities links (Roblox server, CAD, etc.).")
async def links(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Greater Manchester Utilities - Quick Links",
        description="Access all official GMU and ERLC community platforms below:",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="🌐 Roblox Private Server", value="[Click Here to Join](https://www.roblox.com)", inline=False)
    embed.add_field(name="💻 GMU CAD System", value="[Access CAD Portal](https://example.com)", inline=False)
    embed.add_field(name="📜 Community Rules", value="Check our main rules channel.", inline=False)
    embed.set_footer(text="GMU Information System")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not found.")
