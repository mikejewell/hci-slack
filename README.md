# HCI-Slack

HCI-Slack is a set of Django Slack apps used by our HCI research sub-group at ECS (http://www.ecs.soton.ac.uk/). They're all bundled into one project here, but you can easily separate them out if you wish.

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

### General Requirements

HCI-Slack uses Redis for help entries, so you'll need Redis To Go or similar if you're on Heroku. It also requires a few environmental variables, shown below.

* SLACK_WEBHOOK_URL - ingoing webhook URL
* SLACK_GENERAL_CHAT - where work-related messages should go (i.e. help responses)
* SLACK_RANDOM_CHAT - where non-work-related messages should go (i.e. added a track to jukebox)

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

### Miscellanous

slack.utils has a utility function, send_message, which uses the incoming web hook to send a message as any bot, to any channel. The only required parameter is 'text', with username, icon_emoji, icon_url, channel, attachements, and unfurl_links all being optional.
