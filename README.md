# Leaderboard
This code pulls leaderboard data from the API. In order to run this, you need to obtain 
developer credentials from [develop.battle.net](https://develop.battle.net) and put these
in a `secrets` directory.

`secrets/client_id`
`secrets/client_secret`

The script `src/get_access_token.sh` will use these credentials to generate an access_token.
This needs to be updated every 24h (so just rerun get_access_token.sh). 

After building the Docker container, you run it with a mounted volume like so

`docker run -v local_data_dir:/data`

where `local_data_dir` refers to a directory where you want the resulting csv files to appear.
