# Imports for discord
import discord
from discord.ext import commands
from discord import app_commands

# Imports for token
import os
from pathlib import Path
from dotenv import load_dotenv

# The database.py SQLlite
import database

# For the cool data config
from datetime import datetime
from zoneinfo import ZoneInfo

intents = discord.Intents.all()

TutorBOT = commands.Bot(command_prefix='$', intents=intents)

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

# Handles a new server the bot joins while online
@TutorBOT.event
async def on_guild_join(guild: discord.Guild):
    database.add_server(guild.id, guild.name, guild.member_count)

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
    await interaction.response.send_message(
        "Current are sections: " + ", ".join(names)
    )

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
    elif allTasks == 0:
        await interaction.response.send_message(f'Currently there are no logged tasks for {section}')
    else:
        taskMessage = f"Section {section} - Task List \n"
        for task in allTasks:
            taskMessage += f'\n#{task[4]} - {task[0]} - {task[2]}\n'
            taskMessage += f'Due: <t:{task[3]}:R> - Added by @{task[1]}\n'
        await interaction.response.send_message(taskMessage)

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

#Bot token loading and running
load_dotenv(Path(__file__).with_name(".env"))
token = os.getenv("DISCORD_BOT_TOKEN")

TutorBOT.run(token)