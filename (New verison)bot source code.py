from discord.ext import commands
import discord
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import googleapiclient.discovery
import googleapiclient.errors
import os
import googleapiclient.discovery
import urllib.request
import re
import google_auth_oauthlib.flow
import googleapiclient.discovery

scope = "playlist-modify-public"
username = "m0hqkx5sqohmvghs8cqj9oqrg"

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
client_secrets_file = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,scopes=scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

token = SpotifyOAuth(scope=scope, username=username,open_browser=False)
SpotifyObject = spotipy.Spotify(auth_manager=token)
client = commands.Bot(command_prefix=',')

def search_youtube(name):
    html= urllib.request.urlopen("https://www.youtube.com/results?search_query=" +name )
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return video_ids[0]

def main(guild_name):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get credentials and create an API client

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": guild_name,
                "description": "This is a playlist created by Emperor Bot, for more info visit:'https://github.com/newcharhuso/discord-song-request-bot'.",

                "tags": [
                    "Emperor Bot",
                    guild_name

                ],
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    )
    response = request.execute()


def get_youtube_link(guild_name):

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


    request = youtube.playlists().list(
        part="snippet,contentDetails",
        maxResults=25,
        mine=True
    )
    response = request.execute()
    for i in response["items"]:
        if i["snippet"]["title"] == guild_name:
            return (f"https://www.youtube.com/playlist?list={i['id']}")

def get_youtube_playlist_id(guild_name):

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"


    request = youtube.playlists().list(
        part="snippet,contentDetails",
        maxResults=25,
        mine=True
    )
    response = request.execute()
    for i in response["items"]:
        if i["snippet"]["title"] == guild_name:
            return i["id"]


def add_video_to_playlist(youtube, videoID, playlistID):
    add_video_request = youtube.playlistItems().insert(
        part="snippet",
        body={
            'snippet': {
                'playlistId': playlistID,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': videoID
                }

            }
        }
    ).execute()

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
        prePlaylist = SpotifyObject.user_playlists(user=username)
        youtube_keyword = song.replace(" ","+")

        #get playlist link

        def playlist():
            for i in prePlaylist["items"]:
                if i["name"] == guild_name:
                    playlist = i
                    return playlist

        if playlist() != None:
            if playlist()["tracks"]["total"] == 0:

                await ctx.send("Because this bot is new here, creating playlist specific for this channel")
                await ctx.send(f"Here is playlist links: {playlist()['external_urls']['spotify']}")
                await ctx.send(get_youtube_link(guild_name=guild_name))


        try:
            current_tracks = SpotifyObject.user_playlist_tracks(user=username,playlist_id=playlist()["id"])
            list = []
            for i in SpotifyObject.user_playlist_tracks(user=username, playlist_id=playlist()["id"])["items"]:
                list.append(i["track"]["id"])
            if result["tracks"]["items"][0]["id"] in list:
                await ctx.send("Song is already in the list.")

            else:
                SpotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist()["id"], tracks=song_last)
                add_video_to_playlist(youtube=youtube, videoID=search_youtube(name=youtube_keyword),
                                      playlistID=get_youtube_playlist_id(guild_name=guild_name))


                emoji = '\N{THUMBS UP SIGN}'
                await ctx.message.add_reaction(emoji=emoji)


        except:
            SpotifyObject.user_playlist_create(user=username, name=guild_name, public=True)
            main(guild_name=guild_name)

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
    await ctx.send(get_youtube_link(guild_name=guild_name))





client.run(os.environ.get("Client_ID"))