# HCI-Slack

HCI-Slack is a set of Django Slack apps used by our HCI research sub-group at ECS (http://www.ecs.soton.ac.uk/). 

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### Help Entries

Uses a Redis backend to store/retrieve useful information for the group (e.g. links to pages, conference details, etc). 

#### Usage

* /h &lt;key&gt; &lt;value&gt; - creates an entry in the help database (e.g. /h wiki This is our fantastic wiki: <url here>)
* /h &lt;key&gt; - retrieves an entry from the help database (e.g. /h wiki)
* /h list - lists all entry keys
* /h rm &lt;key&gt; - removes an entry from the help database (e.g. /h rm wiki)

#### Required Environmental Variables

* HELP_SLACK_TOKEN: Set this to the value provided by Slack when you create your slash command.

### Jukebox

Uses the Spotify API to add tracks to a shared playlist. This is based on the NodeJS project (https://github.com/benchmarkstudios/slackbox/) but ported over to Django. It requires much the same setup as slackbox: you need create an application on Spotify (https://developer.spotify.com/my-applications).

Once set up, you first need to head to http://yourapp.com/jukebox/authorise. This will store the token in /tmp/jukebox.json, which it'll try to reuse when you add tracks.

#### Usage

* /jukebox &lt;search&gt; - e.g. /jukebox Creep. Adds the first search result to the playlist.

#### Required Environmental Variables

* HELP_SLACK_TOKEN: Set this to the value provided by Slack when you create your slash command.
* SPOTIFY_KEY: The Spotify app's client ID
* SPOTIFY_SECRET: The Spotify app's secret
* SPOTIFY_USERNAME: The user who owns the playlist
* SPOTIFY_PLAYLIST_ID: The ID of the playlist that you're sharing
* SPOTIFY_REDIRECT_URI: Should be http://yoursite.com/jukebox/callback
