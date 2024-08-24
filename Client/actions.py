import discord

async def join_VoiceChannel(interaction: discord.Interaction, force = False) -> bool:
    if interaction.guild is None:
        return False
    User_VoiceState = interaction.user.voice
    Bot_VoiceClient = interaction.guild.voice_client
    if User_VoiceState is not None:
        if Bot_VoiceClient is not None:
            if User_VoiceState.channel.id == Bot_VoiceClient.channel.id:
                return True
            elif User_VoiceState.channel.id != Bot_VoiceClient.channel.id and force == True:
                await Bot_VoiceClient.move_to(User_VoiceState.channel)
        elif Bot_VoiceClient is None:
            await User_VoiceState.channel.connect()
    elif User_VoiceState is None:
        await interaction.channel.send(content = f"No voice channel detected")
    Bot_VoiceClient = interaction.guild.voice_client
    return Bot_VoiceClient is not None

async def leave_VoiceChannel(interaction: discord.Interaction, force = False) -> bool:
    if interaction.guild is None:
        return False
    Bot_VoiceClient = interaction.guild.voice_client
    if Bot_VoiceClient is not None:
        if (
            Bot_VoiceClient.is_playing or
            Bot_VoiceClient.is_paused
        ):
            Bot_VoiceClient.stop()
        await Bot_VoiceClient.disconnect(force = force)
        if Bot_VoiceClient is None:
            await interaction.channel.send(
                content = f"Disconnected from voice channel"
            )
            return True
    return False