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
    return "Project Greater Manchester Bot is active and online!"

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
# Configuration: Update with your link and ERLC code if needed
# -------------------------------------------------------------
ROBLOX_SERVER_LINK = "https://www.roblox.com"
ERLC_SERVER_CODE = "ProjectGM"

# -------------------------------------------------------------
# /session Slash Command Group
# -------------------------------------------------------------
class SessionGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="session", description="Manage Project Greater Manchester sessions")

    @app_commands.command(name="start", description="Start a session")
    async def start(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚡ Project Greater Manchester - Session Started",
            description="The roleplay session has officially commenced! Join the private server and use the code below to enter.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=True)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="low", description="Sends a Low Player Count message")
    async def low(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚠️ Project Greater Manchester - Low Player Count Notice",
            description="Player count in the server is currently low. Additional units and staff are needed!",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=True)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shutdown", description="Shutdown the current session")
    async def shutdown(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛑 Project Greater Manchester - Session Shutdown",
            description="The current session has ended. Thank you to all staff and participants!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vote", description="Start or schedule a session vote")
    @app_commands.describe(duration="Voting duration (e.g. 15 minutes, 30 minutes)", goal="Required vote goal to start session")
    async def vote(self, interaction: discord.Interaction, duration: str = "15 minutes", goal: int = 5):
        embed = discord.Embed(
            title="📊 Project Greater Manchester - Session Vote",
            description=f"Vote below if you want to hold a roleplay session!\n\n**Goal:** {goal} votes required within **{duration}**.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=True)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)
        
        message = await interaction.original_response()
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    @app_commands.command(name="full", description="Sends a Full Server message")
    async def full(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔥 Project Greater Manchester - Server Full Alert",
            description="The server is currently **FULL**! Queue up or wait for a slot to open.",
            color=discord.Color.purple(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=True)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="boost", description="Ask for more players to join the running session")
    async def boost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🚀 Project Greater Manchester - Session Boost Request",
            description="We are seeking additional players to boost the active session! Hop in and support operations.",
            color=discord.Color.dark_orange(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=True)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="config", description="Manage the session config")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You need Administrator permissions to configure session settings.", ephemeral=True)
            return

        embed = discord.Embed(
            title="⚙️ Project Greater Manchester - Session Configuration Panel",
            description="Manage and customize session system configurations.",
            color=discord.Color.dark_grey(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=True)
        embed.add_field(name="Default Vote Goal", value="`5 Votes`", inline=True)
        embed.add_field(name="Server Link", value=f"`{ROBLOX_SERVER_LINK}`", inline=False)
        embed.set_footer(text="Project Greater Manchester Session Control")
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Register the command group
session_group = SessionGroup()
bot.tree.add_command(session_group)

# -------------------------------------------------------------
# Additional Department Commands
# -------------------------------------------------------------
@bot.tree.command(name="announce", description="Post an official department announcement.")
@app_commands.describe(title="Announcement Title", message="Announcement content")
async def announce(interaction: discord.Interaction, title: str, message: str):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📢 Project Greater Manchester Notice: {title}",
        description=message,
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="Project Greater Manchester | Utilities Division")
    
    await interaction.response.send_message("Announcement posted successfully!", ephemeral=True)
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="links", description="Get official Project Greater Manchester links (Roblox server, CAD, etc.).")
async def links(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Project Greater Manchester - Quick Links",
        description="Access all official platforms below:",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="🔑 ERLC Server Code", value=f"`{ERLC_SERVER_CODE}`", inline=False)
    embed.add_field(name="🌐 Roblox Private Server", value=f"[Click Here to Join]({ROBLOX_SERVER_LINK})", inline=False)
    embed.add_field(name="💻 CAD System", value="[Access CAD Portal](https://example.com)", inline=False)
    embed.add_field(name="📜 Community Rules", value="Check our main rules channel.", inline=False)
    embed.set_footer(text="Project Greater Manchester Information System")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Project Greater Manchester Bot logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not found.")
