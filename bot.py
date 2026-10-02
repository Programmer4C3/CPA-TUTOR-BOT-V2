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

@app_commands.command(name='add_task', description="Add a type of coursework to the db date format (MM/DD/YY)")
async def add_task(interaction: discord.Interaction, course:str, title:str, section:str, date:int):
    sectionFound = database.add_task(section, interaction.guild_id, title, interaction.user.name, course, date)

    if sectionFound == -1:
        await interaction.response.send_message(f'The section {section} does not exist!')
    elif sectionFound == 0:
        await interaction.response.send_message(f'The section {section} has reached task limits')
    else:
        await interaction.response.send_message(f'Sucessfully added "{title}" from {course} to section: {section} that is due on the {date}')

TutorBOT.tree.add_command(add_task)

@app_commands.command(name='display_task', description="View all due tasks for a section.")
async def display_task(interaction: discord.Interaction, section:str):
    allTasks = database.display_tasks(section, interaction.guild_id)

    if allTasks == -1:
        await interaction.response.send_message(f'Are you sure {section} exists?')
    elif allTasks == 0:
        await interaction.response.send_message(f'Currently there are no logged tasks for {section}')
    else:
        taskMessage = f"Here are the current items due for {section}: \n"
        for task in allTasks:
            taskMessage += f'[ID:{task[4]}] {task[0]} from {task[2]} is due on {task[3]} - **{task[1]}**\n'
        await interaction.response.send_message(taskMessage)

TutorBOT.tree.add_command(display_task)

@app_commands.command(name='remove_task', description="remove a due task for a section via taskID.")
async def remove_task(interaction: discord.Interaction, section:str, taskid:int):
    await interaction.response.send_message(f'Item has been removed')

TutorBOT.tree.add_command(remove_task)

load_dotenv(Path(__file__).with_name(".env"))
token = os.getenv("DISCORD_BOT_TOKEN")

TutorBOT.run(token)