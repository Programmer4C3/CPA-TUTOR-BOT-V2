# Imports for discord
import discord
from discord.ext import commands, tasks
from discord import app_commands

# Imports for token
import os
from pathlib import Path
from dotenv import load_dotenv

# The database.py SQLlite
import database

# The questions.json file
import questions

# For the cool data config
from datetime import datetime
from zoneinfo import ZoneInfo

intents = discord.Intents.all()

TutorBOT = commands.Bot(command_prefix='$', intents=intents)

TutorBOT.tree.allowed_contexts = app_commands.AppCommandContext(
    guild=True,
    dm_channel=False,
    private_channel=False
)

@app_commands.allowed_installs(guilds=True, users=True)

@TutorBOT.event
async def on_ready():
    for guild in TutorBOT.guilds:
        database.add_server(guild.id, guild.name, guild.member_count)

    try:
        synced = await TutorBOT.tree.sync()
        print(f'Synced {len(synced)} commands(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

    print(f'Logged in as {TutorBOT.user.name}')

    if not scheduled_checks.is_running():
        scheduled_checks.start()

    for guild in TutorBOT.guilds:
        print(f"Connected to: {guild.name} ({guild.id})")

# Handles a new server the bot joins while online
@TutorBOT.event
async def on_guild_join(guild: discord.Guild):
    database.add_server(guild.id, guild.name, guild.member_count)

@app_commands.command(name='set_bypass', description="Set a role to bypass commands")
async def set_bypass(interaction: discord.Interaction, role_id:discord.Role):
    database.set_bypass(interaction.guild_id, role_id.id)

TutorBOT.tree.add_command(set_bypass)

@app_commands.command(name='get_settings', description="See all settings for the server")
async def get_settings(interaction: discord.Interaction):
    allSettings = database.get_settings(interaction.guild_id)

    embed = discord.Embed(
        title=f"⚙️ {interaction.guild}\'s Settings ⚙️",
        colour = discord.Colour.purple()
    )

    message = ""

    for setting, status in allSettings.items():
        if setting.startswith("restricted"):
            status = "Enabled" if status else "Disabled"
        elif status is None:
            status = "Not set"

        message += f"**{setting}** : {status}\n"

        if setting in ("memberCount", "restrictedAddSection", "updateChannel"):
            message += "\n"

    embed.description = message

    await interaction.response.send_message(embed=embed)

TutorBOT.tree.add_command(get_settings)

def canUserBypass(server_id:int, userRoles:tuple):
    byPassRole = database.checkBypass(server_id)
    if byPassRole is not None:
        for role in userRoles:
            if role.id == byPassRole:
                return True
        return False

@app_commands.command(name='add_section', description="Add a new section with a realtionship to this server.")
async def add_section(interaction: discord.Interaction, section_name:str):
    database.add_section(interaction.guild_id, section_name)

    await interaction.response.send_message(f'Section "{section_name}" has been added!')

TutorBOT.tree.add_command(add_section)

@app_commands.command(name='display_section', description="Display all available sections in this server.")
async def display_section(interaction: discord.Interaction):
    rows = database.display_section(interaction.guild_id)

    if not rows:
        await interaction.response.send_message(f'No available sections for this server yet!')
        return

    names = [row[0] for row in rows]

    embed = discord.Embed(
        title=f"🌧️ {interaction.guild}\'s Sections 🌧️",
        description="\n".join(names),
        colour = discord.Colour.yellow()
    )

    await interaction.response.send_message(embed=embed)

TutorBOT.tree.add_command(display_section)

@app_commands.command(name='add_task', description="Add a task to a particular section with a due date (MM/DD/YYYY) XX:XX PM/AM")
async def add_task(interaction: discord.Interaction, course:str, title:str, section:str, date:str, time:str):
    #Attempting to convert the date into a int
    try:
        cleanTime = time.replace(" ", "").upper()

        due = datetime.strptime(
            f"{date} {cleanTime}",
            "%m/%d/%Y %I:%M%p"
        )

        due = due.replace(tzinfo=ZoneInfo("America/Toronto"))
        due_timestamp = int(due.timestamp())     

        result = database.add_task(section, interaction.guild_id, title, interaction.user.name, course, due_timestamp)

        await interaction.response.send_message(result)   
    except ValueError:
        await interaction.response.send_message("Use a format similiar to: 10/22/2026 and a time like 8:30 PM ")

TutorBOT.tree.add_command(add_task)

@app_commands.command(name='display_task', description="View all due tasks for a section.")
async def display_task(interaction: discord.Interaction, section:str):
    allTasks = database.display_tasks(section, interaction.guild_id)

    if allTasks == -1:
        await interaction.response.send_message(f'Are you sure {section} exists?')
    else:
        embed = discord.Embed(
            title=f"📚 Section {section}\'s Tasks 📚",
            colour = discord.Colour.blue()
        )

        if allTasks == 0:
            embed.description = "None"
            embed.set_footer(text=f"0 task(s)")
            await interaction.response.send_message(embed=embed)
            return
        else:
            for taskID, taskName, courseName, addedBy, dueDate in allTasks:
                embed.add_field(
                    name=f"#{taskID} · {taskName} | {courseName}",
                    value=(
                        f"Due <t:{dueDate}:R>\n"
                        f"Added by <@{addedBy}>"
                    ),
                    inline=False,
                )

            embed.set_footer(text=f"{len(allTasks)} task(s)")

        await interaction.response.send_message(embed=embed)

TutorBOT.tree.add_command(display_task)

@app_commands.command(name='remove_task', description="remove a due task for a section via taskID.")
async def remove_task(interaction: discord.Interaction, section:str, task_id:int):
    result = database.remove_task(task_id,section,interaction.guild_id)

    await interaction.response.send_message(result)

TutorBOT.tree.add_command(remove_task)

@app_commands.command(name='clear_tasks', description="remove all tasks for a section")
async def clear_tasks(interaction: discord.Interaction, section:str):
    result = database.clear_tasks(section, interaction.guild_id)

    await interaction.response.send_message(result)

TutorBOT.tree.add_command(clear_tasks)

@app_commands.command(name='remove_section', description="remove a section via sectionName")
async def remove_section(interaction: discord.Interaction, section:str):
    result = database.remove_section(section, interaction.guild_id)

    await interaction.response.send_message(result)

TutorBOT.tree.add_command(remove_section)

@app_commands.command(name='set_restriction', description="set a restriction config to a certain status")
async def set_restriction(interaction: discord.Interaction, restriction_type:str, status:bool):
    if not canUserBypass(interaction.guild_id, interaction.user.roles):
        await interaction.response.send_message(f"Only <@&{database.checkBypass(interaction.guild_id)}> can use this command")
        return

    result = database.set_restriction(interaction.guild_id, restriction_type, status)

    await interaction.response.send_message(result)

TutorBOT.tree.add_command(set_restriction)

@app_commands.command(name='set_channel', description="set a certain channel for the bot's specific message")
async def set_channel(interaction: discord.Interaction, channel_type:str, location:discord.TextChannel):
    if not canUserBypass(interaction.guild_id, interaction.user.roles):
        await interaction.response.send_message(f"Only <@&{database.checkBypass(interaction.guild_id)}> can use this command")
        return
    
    result = database.set_channel(interaction.guild_id, channel_type, location.id)

    await interaction.response.send_message(result)

TutorBOT.tree.add_command(set_channel)

# Loop functions
@tasks.loop(minutes=1)
async def scheduled_checks():
    ## Task deletion message!
    allExpired = database.remove_expired_tasks()
    
    for taskName, sectionName, serverId in allExpired:
        serverSettings = database.get_settings(serverId)

        if serverSettings is None or serverSettings["updateChannel"] is None:
            continue

        channel = TutorBOT.get_channel(serverSettings["updateChannel"])

        if channel is None:
            continue

        try:
            await channel.send(
                f'⏰ **{taskName}** in Section: **{sectionName}** is now past it\'s due date and has been removed!'
            )
        except discord.HTTPException as error:
            print(f"Could not send task update for {serverId}: {error}")

    #Morning update code
    now = datetime.now(ZoneInfo("America/Toronto"))
    if now.hour == 8 and now.minute == 00:
        for guild in TutorBOT.guilds:
            serverSettings = database.get_settings(guild.id)

            if serverSettings is None or serverSettings["morningChannel"] is None:
                continue

            channel = guild.get_channel(serverSettings["morningChannel"])

            if channel is None:
                continue

            try:
                await channel.send("☀️ Good morning, CPA!")
            except discord.HTTPException as error:
                print(f"Could not send greeting in {guild.name}: {error}")
    elif now.hour == 13 and now.minute == 00:
        question = questions.get_question()

        for guild in TutorBOT.guilds:
            serverSettings = database.get_settings(guild.id)

            if serverSettings is None or serverSettings["questionChannel"] is None:
                continue

            channel = guild.get_channel(serverSettings["morningChannel"])

            if channel is None:
                continue

            try:
                message = "🧠 **Programming Question of the Day** 🧠\n"
                message += f"{question['question']}"
                await channel.send(message)
                questions.remove_question(question["id"])
            except discord.HTTPException as error:
                print(f"Could not send greeting in {guild.name}: {error}")
        

#Bot token loading and running
load_dotenv(Path(__file__).with_name(".env"))
token = os.getenv("DISCORD_BOT_TOKEN")

TutorBOT.run(token)