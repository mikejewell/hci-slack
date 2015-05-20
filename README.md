HCI-Slack is a set of Django Slack apps used by our HCI research sub-group at ECS (http://www.ecs.soton.ac.uk/). Currently this includes:

* help: Uses a Redis backend to store/retrieve useful information for the group (e.g. links to pages, conference details, etc). 
* jukebox: Uses the Spotify API to add tracks to a shared playlist. This is based on the NodeJS project (https://github.com/benchmarkstudios/slackbox/) but ported over to Django.
