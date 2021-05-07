from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

scope = "playlist-modify-public"
username = "m0hqkx5sqohmvghs8cqj9oqrg"

token = SpotifyOAuth(scope=scope, username=username,open_browser=False)
SpotifyObject = spotipy.Spotify(auth_manager=token)
client = commands.Bot(command_prefix=',')


@client.event
async def on_ready():
    print("Bot is ready")


@client.command()
async def add(ctx):
    try:
        song = ctx.message.content.replace(",add", "")
        result = SpotifyObject.search(q=song)
        song_last = []
        song_last.append(result["tracks"]["items"][0]["uri"])
        guild_name = ctx.guild.name
        desc = f"This is a playlist created spesific for influencer {guild_name}"
        prePlaylist = SpotifyObject.user_playlists(user=username)


        def playlist():
            for i in prePlaylist["items"]:
                if i["name"] == guild_name:
                    playlist = i
                    return playlist

        if playlist() != None:
            if playlist()["tracks"]["total"] == 0:

                await ctx.send("Because this bot is new here, creating playlist specific for this channel")
                await ctx.send(f"Here is playlist link: {playlist()['external_urls']['spotify']}")

        try:
            current_tracks = SpotifyObject.user_playlist_tracks(user=username,playlist_id=playlist()["id"])
            list = []
            for i in SpotifyObject.user_playlist_tracks(user=username, playlist_id=playlist()["id"])["items"]:
                list.append(i["track"]["id"])
            if result["tracks"]["items"][0]["id"] in list:
                await ctx.send("Song is already in the list.")

            else:
                SpotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist()["id"], tracks=song_last)
                emoji = '\N{THUMBS UP SIGN}'
                await ctx.message.add_reaction(emoji=emoji)


        except:
            SpotifyObject.user_playlist_create(user=username, name=guild_name, public=True)
    except:
        await ctx.send("Couldn't find the song you are looking for.")

@client.command()
async def link(ctx):
    guild_name = ctx.guild.name
    prePlaylist = SpotifyObject.user_playlists(user=username)
    def playlist():
        for i in prePlaylist["items"]:
            if i["name"] == guild_name:
                playlist = i
                return playlist
    await ctx.send(playlist()['external_urls']['spotify'])








client.run(os.environ.get("Client_ID"))