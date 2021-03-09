import discord
from string import Template
from discord.ext import commands
from inhouse_bot.database_orm import Game

VOICE_CATEGORY = '▬▬ Team Voice Chat ▬▬'
public_channel = '-- Game #$game_id --'
team_channel = '--> $side Team #$game_id'


async def create_voice_channels(ctx: commands.Context, game: Game):
    """
    Creates a private voice channel for each team of players in a game and a public
    voice channel for all to join
    """

    category = discord.utils.get(ctx.guild.categories, name=VOICE_CATEGORY)
    # Creates the category for Team Voice Chat if it doesn't exist
    if category is None:
        category = await discord.Guild.create_category(ctx.guild, VOICE_CATEGORY)

    # Creates a public channel that also acts as a header for the team voice channels
    await discord.Guild.create_voice_channel(
        ctx.guild,
        name=Template(public_channel).substitute(game_id=game.id),
        category=category,
    )

    for side in ("BLUE", "RED"):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }

        for p in getattr(game.teams, side):
            member = discord.Guild.get_member(ctx.guild, p.id)
            if member is not None:
                overwrites[member] = discord.PermissionOverwrite(read_messages=True)

        await discord.Guild.create_voice_channel(
            ctx.guild,
            name=Template(team_channel).substitute(side=side.capitalize(), game_id=game.id),
            category=category,
            overwrites=overwrites
        )


async def remove_voice_channels(ctx: commands.Context, game: Game):
    """
    Removes all voice channels associated with a game
    """

    for channel in [
        Template(public_channel).substitute(game_id=game.id),
        Template(team_channel).substitute(side="Blue", game_id=game.id),
        Template(team_channel).substitute(side="Red", game_id=game.id)
    ]:
        channel_to_del = discord.utils.get(ctx.guild.channels, name=channel)
        if channel_to_del is not None:
            await channel_to_del.delete()
