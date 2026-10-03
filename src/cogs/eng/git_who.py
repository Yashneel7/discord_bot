from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands

from src.cogs.eng.groups import EngGroups
from src.utils import decorators as bot_decorators

if TYPE_CHECKING:
    from src.bot import DiscordBot


class EngGitCommands:
    client: DiscordBot

    @EngGroups.eng_git.command(name="who", description="Identify a given user")
    @app_commands.describe(
        member="Discord member to look up",
        github_username="GitHub username to look up",
    )
    @bot_decorators.defer(ephemeral=False)
    @bot_decorators.requires_location(bot_decorators.CommandLocation.GUILD)
    @bot_decorators.requires_roles(bot_decorators.FunctionalRole.DEV_ENGINEER)
    @bot_decorators.handle_command_errors()
    async def who(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
        github_user: str | None = None,
    ) -> None:
        if github_user is not None:
            username = (github_user.strip()).lower()
            linked = self.client.stores.git_links.find_one(github_username=username)
            target = github_user
        elif member is not None:
            disc_id = member.id
            linked = self.client.stores.git_links.find_one(discord_user_id=disc_id)
            target = member.mention
        elif github_user is None and member is None:
            await interaction.followup.send(
                content="Please provide either a member or a github_username, not both or neither."
            )
            return
        if linked is None:
            await interaction.followup.send(
                content=f"No linked GitHub account found for {target}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        await interaction.followup.send(
            content=f"<@{linked.discord_user_id}> (ID: {linked.discord_user_id}) is {linked.github_username}"
        )
