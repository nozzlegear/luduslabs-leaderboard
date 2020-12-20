current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#echo $current_dir/../secrets/client_id
client_id=$(cat $current_dir/../secrets/client_id)
client_secret=$(cat $current_dir/../secrets/client_secret)
curl -u $client_id:$client_secret -d grant_type=client_credentials https://us.battle.net/oauth/token > $current_dir/../secrets/access_token
