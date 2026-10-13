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
# Configuration: Update with your details
# -------------------------------------------------------------
ROBLOX_SERVER_LINK = "https://www.roblox.com"
ERLC_SERVER_CODE = "ProjectGM"
STAFF_ROLE_ID = 1559605936887173250 # Staff role ID for pings, permissions, and ticket claiming

# -------------------------------------------------------------
# Ticket System Components
# -------------------------------------------------------------
class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.success, emoji="🙋‍♂️", custom_id="claim_ticket_btn")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has the staff role or manage messages permission
        has_role = any(role.id == STAFF_ROLE_ID for role in interaction.user.roles)
        
        if not (has_role or interaction.user.guild_permissions.manage_messages):
            await interaction.response.send_message("You do not have permission to claim this ticket.", ephemeral=True)
            return

        # Restrict other staff members from messaging in this channel
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            await interaction.channel.set_permissions(staff_role, send_messages=False)
        
        # Grant explicit permission to the claiming staff member
        await interaction.channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        # Disable claim button and update label
        button.disabled = True
        button.label = f"Claimed by {interaction.user.display_name}"
        button.style = discord.ButtonStyle.secondary

        # Update embed to show claimed status
        embed = interaction.message.embeds[0]
        embed.add_field(name="Claimed By", value=interaction.user.mention, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(f"Ticket successfully claimed by {interaction.user.mention}!")

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing this ticket in 5 seconds...")
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

class TicketModal(discord.ui.Modal, title="Open Support Ticket"):
    subject = discord.ui.TextInput(
        label="Subject / Topic",
        placeholder="e.g., General Support, Report, Department Inquiry",
        required=True
    )
    details = discord.ui.TextInput(
        label="How can staff help you today?",
        style=discord.TextStyle.paragraph,
        placeholder="Provide as much detail as possible...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        # Strict permission overwrites: Deny everyone else, allow only the user and staff role
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        staff_role = guild.get_role(STAFF_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Create ticket channel under a category if possible
        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            category = await guild.create_category("TICKETS")

        channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"🎫 Support Ticket - {self.subject.value}",
            description=f"Welcome {user.mention}! A staff member will be with you shortly.\n\n**Reason:**\n{self.details.value}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="Project Greater Manchester | Ticket System")

        ping_content = f"<@&{STAFF_ROLE_ID}>"

        await ticket_channel.send(content=ping_content, embed=embed, view=TicketControlView())
        await interaction.response.send_message(
            f"Ticket created! Head over to {ticket_channel.mention} to talk with staff.", 
            ephemeral=True
        )

class CreateTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.primary, emoji="📩", custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

# Ticket Panel Slash Command
@bot.tree.command(name="ticket-panel", description="Post the support ticket panel embed (Admin only).")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need Administrator permissions to set up the ticket panel.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📩 Project Greater Manchester - Support Tickets",
        description="Need assistance, have a question, or want to report an issue?\n\nClick the **Open Ticket** button below to create a private support ticket with our staff team.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Project Greater Manchester Support")
    
    await interaction.channel.send(embed=embed, view=CreateTicketView())
    await interaction.response.send_message("Ticket panel posted successfully!", ephemeral=True)

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
    # Register persistent views so buttons keep working after bot restarts
    bot.add_view(CreateTicketView())
    bot.add_view(TicketControlView())
    await bot.tree.sync()
    print(f"Project Greater Manchester Bot logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN environment variable not found.")
