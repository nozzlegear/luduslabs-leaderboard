SEASON=30
BRACKETS=(2v2 3v3)
ZONES=(eu us)

./get_access_token.sh

code_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
data_dir=$(echo $code_dir/../data)
token=$(cat ../secrets/access_token | cut -f 1 --delimiter ","|cut -f 2 -d ":"|sed --expression='s/"//g')


auth=$(echo "Authorization: Bearer" $token)


todays_date=$(date +"%Y%m%d")

for BRACKET in ${BRACKETS[@]};
do
    for ZONE in ${ZONES[@]};
    do
	cd $code_dir
	# Get ladder data; this is a single API call so we just do it with curl
	#curl -o $data_dir/${ZONE}_${BRACKET}_ladder_${todays_date}.json --header "$auth" \
	#     https://${ZONE}.api.blizzard.com/data/wow/pvp-season/${SEASON}/pvp-leaderboard/${BRACKET}?namespace=dynamic-${ZONE}&locale=en_US 

	# Convert to a more workable format
	python3 process_ladder_data.py \
		${data_dir}/${ZONE}_${BRACKET}_ladder_${todays_date}.json \
		$data_dir/${ZONE}_${BRACKET}_ladder_${todays_date}.csv

	# The ladder data is missing a bunch of character-specific information (e.g. class)
	# so we need to fetch this with API calls
	cd $data_dir
	rm -r tmp
	mkdir tmp

	# Get a list of all the names and realms for each person
	cat ${ZONE}_${BRACKET}_ladder_${todays_date}.json |jq .entries[] \
	    | jq '.character|{name, realm}' > tmp/${ZONE}_${BRACKET}_ladder_chars.json

	# Get name and server for each person on the ladder
	cat tmp/${ZONE}_${BRACKET}_ladder_chars.json \
	    | jq .name > tmp/${ZONE}_${BRACKET}_char_name
	
	cat tmp/${ZONE}_${BRACKET}_ladder_chars.json \
	    | jq .realm | jq .slug > tmp/${ZONE}_${BRACKET}_char_realm

	# Glue together into a single file; prep for API calls
	paste tmp/${ZONE}_${BRACKET}_char_name tmp/${ZONE}_${BRACKET}_char_realm -d ',' \
	      > tmp/${ZONE}_${BRACKET}_names_realms
	

	# Run requests against Blizzard API to get character data for those
	# on the ladder
	python3 ../src/get_api_character_requests.py \
		tmp/${ZONE}_${BRACKET}_names_realms \
		tmp/${ZONE}_${BRACKET}_char_${todays_date}.json $token
	
	# Tidy the character data up
	python3 ../src/process_character_data.py \
		tmp/${ZONE}_${BRACKET}_char_${todays_date}.json \
		${ZONE}_${BRACKET}_char_${todays_date}.csv

	# Join ladder data and character data together
	python3 ../src/join_datasets_on_key.py \
		${ZONE}_${BRACKET}_ladder_${todays_date}.csv \
		${ZONE}_${BRACKET}_char_${todays_date}.csv \
		id \
		${ZONE}_${BRACKET}_combined_${todays_date}.csv

    done;
done;
