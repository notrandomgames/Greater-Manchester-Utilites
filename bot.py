import discord
from discord import app_commands
from discord.ext import commands
import datetime
import os
from flask import Flask
import threading

# Initialize Flask web server for Render keep-alive
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

# -------------------------------------------------------------
# /session Slash Command Group (Central & ERM style)
# -------------------------------------------------------------
class SessionGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="session", description="Manage Greater Manchester Utilities server sessions")

    @app_commands.command(name="start", description="Start a session")
    async def start(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ Greater Manchester Utilities - Session Started",
            description="The GMU Roleplay session has officially commenced! Join the server below to take part in utility operations across Greater Manchester.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🌐 Roblox Private Server", value="[Click Here to Join Server](https://www.roblox.com)", inline=False)
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="low", description="Sends a Low Player Count message")
    async def low(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚠️ GMU Session - Low Player Count Notice",
            description="Player count in the GMU server is currently low. Additional field units and utility technicians are needed to keep operations active!",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🌐 Join Server", value="[Click Here to Join Server](https://www.roblox.com)", inline=False)
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shutdown", description="Shutdown the current session")
    async def shutdown(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛑 Greater Manchester Utilities - Session Shutdown",
            description="The current utility roleplay session has ended. Thank you to all GMU staff and emergency personnel who participated!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vote", description="Start or schedule a session vote")
    @app_commands.describe(duration="Voting duration (e.g. 15 minutes, 30 minutes)", goal="Required vote goal to start session")
    async def vote(self, interaction: discord.Interaction, duration: str = "15 minutes", goal: int = 5):
        embed = discord.Embed(
            title="📊 Greater Manchester Utilities - Session Vote",
            description=f"Vote below if you want to hold a GMU roleplay session!\n\n**Goal:** {goal} votes required within **{duration}**.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)
        
        # Add default vote reactions
        message = await interaction.original_response()
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @app_commands.command(name="full", description="Sends a Full Server message")
    async def full(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔥 GMU Session - Server Full Alert",
            description="The Greater Manchester Utilities server is currently **FULL**! Queue up or wait for a slot to open.",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="boost", description="Ask for more players to join the running session")
    async def boost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 Session Boost Request!",
            description="We are seeking additional players to boost the active session! Hop into Greater Manchester and support active grid operations.",
            color=discord.Color.dark_orange(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🌐 Join Server", value="[Click Here to Join Server](https://www.roblox.com)", inline=False)
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="config", description="Manage the session config")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need Administrator permissions to configure session settings.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ GMU Session Configuration Panel",
            description="Manage and customize session system configurations for Greater Manchester Utilities.",
            color=discord.Color.dark_grey(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Session Ping Role", value="`Not Configured`", inline=True)
        embed.add_field(name="Default Vote Goal", value="`5 Votes`", inline=True)
        embed.add_field(name="Server Link", value="`Set in Code`", inline=True)
        embed.set_footer(text="GMU Session Control | Central & ERM Standard")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Register the command group
session_group = SessionGroup()
bot.tree.add_command(session_group)

# -------------------------------------------------------------
# Additional Department Commands
# -------------------------------------------------------------
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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Greater Manchester Utilities Bot logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not found.")
