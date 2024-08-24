import asyncio
import copy
from typing import Callable
from Common import conversion
import discord
from discord.ext import commands
from discord import app_commands
from Client import actions
from AudioSources.source import sourcecls

class _Player:
    ffmpegopts = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 15',
                'options': '-vn -filter:a "volume=0.25"'
    }

    def __init__(self, bot: commands.Bot, interaction: discord.Interaction, cleanup: Callable[..., None]):
        self.bot = bot
        self.interaction = interaction
        self.guild = interaction.guild
        self.channel = interaction.channel
        self.queue = asyncio.Queue()
        self.is_playing = asyncio.Event()
        self.now_playing = None
        self.cleanup = cleanup
        self.task = asyncio.create_task(self.play_task())
        self.task.add_done_callback(self.handle_play_task)

    def handle_play_task(self, task):
        if task.exception():
            print(
                f"[play_task] Task exception:\n"
                f"{task.exception()}"
            )
            pass

    async def play_task(self):
        print("[play_task] started")
        while True:
            await asyncio.sleep(1)
            await self.bot.wait_until_ready()
            if not isinstance(self.queue, asyncio.Queue):
                print("Not found: queue instance")
                await self.channel.send("Queue not found")
                return
            try:
                source_info = await asyncio.wait_for(
                    self.queue.get(),
                    15
                )
            except Exception as e:
                source_info = None
                print(f"Queue exception: {e}")
                #await self.channel.send("Queue failed")
            # Recreate sourcecls
            if source_info is not None:
                cls_source = sourcecls(
                    requestor = source_info['requestor'],
                    query = source_info['query'],
                    platform = source_info['platform'],
                    source_info = source_info
                )
                if not await asyncio.to_thread(cls_source.refresh):
                    continue
                # Play
                try:
                    ffmpeg_source = discord.FFmpegPCMAudio(
                        source = cls_source.source_info['source'].get('url'),
                        **self.ffmpegopts
                    )
                except Exception as e:
                    print(f"FFmpegPCMAudio exception: {e}")
                    await self.channel.send("Audio failed.")
                    continue
                try:
                    self.is_playing.clear()
                    self.guild.voice_client.play(
                        source = ffmpeg_source,
                        after = lambda _: self.is_playing.set()
                    )
                except Exception as e:
                    print("guild.voice_client.play FFmpegPCMAudio exception")
                    print(str(e))
                    self.guild.voice_client.stop()
                    ffmpeg_source._kill_process()
                    continue
                self.now_playing = (
                    f"Now playing\n"
                    f"{cls_source.source_info['source'].get('webpage_url')}"
                )
                await self.channel.send(self.now_playing)
                while (
                    not self.is_playing.is_set() and
                    self.guild.voice_client is not None and
                    len(self.guild.voice_client.channel.members) > 1 and
                    (
                        self.guild.voice_client.is_playing or
                        self.guild.voice_client.is_paused
                    )
                ):
                    await asyncio.sleep(1)
                self.now_playing = None
                self.guild.voice_client.stop()
                ffmpeg_source.cleanup()
            for _ in range(600):
                if self.queue.empty():
                    await asyncio.sleep(1)
                else:
                    break
            if self.queue.empty() or len(self.guild.voice_client.channel.members) <= 1:
                print("Queue is empty or bot is alone > stop playing")
                await actions.leave_VoiceChannel(
                    interaction = self.interaction,
                    force = False
                )
                if isinstance(cls_source, sourcecls):
                    del cls_source
                await self.cleanup(guild_id = self.guild.id)
                return

# Cog
class Player(commands.Cog):
    guild_players = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("commands.Cog loaded")

    async def cleanup(self, guild_id: int):
        if guild_id in self.guild_players:
            try:
                print("Cleaning up")
                player = self.guild_players.get(guild_id)
                del player
                del self.guild_players[guild_id]
            except Exception as e:
                print(f"cleanup exception: {e}")

    async def get_guild_player(self, interaction: discord.Interaction):
        if interaction.guild_id in self.guild_players:
            player = self.guild_players.get(interaction.guild_id)
        else:
            player = _Player(
                bot = self.bot,
                interaction = interaction,
                cleanup = self.cleanup
            )
            self.guild_players[interaction.guild_id] = player
        if player is None or not isinstance(player, _Player):
            print("Not found: _Player instance")
            return None
        return player

    def handle_resolve_queries_task(self, task):
        if task.exception():
            print(
                f"[resolve_queries_task] Task exception:\n"
                f"{task.exception()}"
            )
            pass

    async def resolve_queries_task(self, interaction: discord.Interaction, query: str, platform: str, player: _Player, playliststart = 1, playlistend = 1):
        print("[resolve_queries_task] started")
        await asyncio.sleep(1)
        _source_list = sourcecls(
                requestor = interaction.user.name,
                query = query,
                platform = platform,
                source_info = None
            )
        playlist = 1
        playlistmax = playliststart+playlistend
        while playlist is not None:
            source_list = await asyncio.to_thread(_source_list.get, playliststart, playlistend)
            playliststart = playlistend+1
            playlistend += playlistmax
            if isinstance(source_list, list) and len(source_list) > 0:
                # Enqueue
                msg_content = ""
                for source_info in source_list:
                    if source_info is None:
                        continue
                    playlist = source_info['source'].get('playlist_count')
                    try:
                        player.queue.put_nowait(
                            copy.deepcopy(
                                source_info
                            )
                        )
                        # Notification
                        if source_info['source'].get('duration') is not None:
                            print(f"[resolve_queries_task] duration `{source_info['source'].get('duration')}`")
                            duration = await conversion.SecondsToString(source_info['source'].get('duration'))
                        else:
                            duration = "0"
                        print(f"[resolve_queries_task] duration `{duration}`")
                        msg_content += (
                                f"#{player.queue.qsize()} {source_info['source'].get('title')} `{duration}` \U00002705\n"
                        )
                        if len(msg_content) > 2500:
                            await interaction.channel.send(content = msg_content)
                            msg_content = ""
                    except asyncio.QueueFull:
                        await interaction.channel.send(content = f"Queue is full")
                        pass
                    except Exception as e:
                        print(f"An exception occurred: {e}")
                        pass
                # Notify
                if len(msg_content) > 0:
                    await interaction.channel.send(content = msg_content)
            else:
                break
        # Cleanup
        try:
            if isinstance(source, sourcecls):
                    del source
            if isinstance(player, _Player):
                del player
        except:
            pass
        print("[resolve_queries_task] finished")

    # Commands
    @app_commands.command(name = "play", description = "Play a song")
    @app_commands.choices(platform=[
        app_commands.Choice(name = "Auto", value = "auto"),
        app_commands.Choice(name = "Soundcloud", value = "Soundcloud"),
    ])
    async def play(self, interaction: discord.Interaction, query: str, platform: app_commands.Choice[str] = None):
        if platform is None:
            platform = app_commands.Choice(name="Auto", value="auto")
        await interaction.response.send_message(content = f"`{query}`")
        if not await actions.join_VoiceChannel(
                interaction = interaction,
                force = False
        ):
            return
        # Initiate task
        player = await self.get_guild_player(interaction = interaction)
        if isinstance(player, _Player):
            task = asyncio.create_task(
                self.resolve_queries_task(
                    interaction = interaction,
                    query = query,
                    platform = platform.value,
                    player = player,
                    playliststart = 1,
                    playlistend = 10
                )
            )
            task.add_done_callback(self.handle_resolve_queries_task)
        else:
            await interaction.channel.send(content = f"Player failed")
        # Cleanup
        try:
            if isinstance(player, _Player):
                del player
        except:
            pass
        print("[play] finished")

    @app_commands.command(name = "stop", description = "Stop playing")
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.send_message(content = f"Stopping")
        player = await self.get_guild_player(interaction = interaction)
        if player is None:
            return
        while not player.queue.empty():
            try:
                player.queue.get_nowait()
                player.queue.task_done()
            except:
                pass
        player.is_playing.set()
        if isinstance(player, _Player):
            del player

    @app_commands.command(name = "skip", description = "Skip song")
    async def skip(self, interaction: discord.Interaction):
        await interaction.response.send_message(content = f"Skipping")
        player = await self.get_guild_player(interaction = interaction)
        try:
            player.is_playing.set()
        except Exception as e:
            print(f"An exception occurred: {e}")
        finally:
            if isinstance(player, _Player):
                del player

    @app_commands.command(name = "np", description = "Now playing information")
    async def np(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        player = await self.get_guild_player(interaction = interaction)
        try:
            if not bool(player.now_playing):
                await interaction.followup.send(
                    content = str(player.now_playing)
                )
        except:
            pass
        finally:
            if isinstance(player, _Player):
                del player

    @app_commands.command(name = "reload", description = "Reload cogs if the bot gets stuck")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await self.bot.reload_extension("Cogs.player")
        await interaction.followup.send(content = "Reloaded")

async def setup(bot: commands.Bot):
    print("Adding cog...")
    await bot.add_cog(Player(bot))



