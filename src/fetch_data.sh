#!/bin/bash

SEASON=31
BRACKETS=(2v2 3v3 rbg)
ZONES=(eu us)


code_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
${code_dir}/get_access_token.sh

data_dir=/data
token=$(cat ../secrets/access_token | cut -f 1 --delimiter ","|cut -f 2 -d ":"|sed --expression='s/"//g')

auth=$(echo "Authorization: Bearer" $token)

mkdir $data_dir/.tmp

todays_date=$(date +"%Y%m%d")

for BRACKET in ${BRACKETS[@]};
do
    for ZONE in ${ZONES[@]};
    do

	until $(curl -o $data_dir/.tmp/${todays_date}_${ZONE}_${BRACKET}_ladder.json \
		     --header "$auth" \
		     https://${ZONE}.api.blizzard.com/data/wow/pvp-season/${SEASON}/pvp-leaderboard/${BRACKET}?namespace=dynamic-${ZONE}&locale=en_US); do
	    printf '.'
	    sleep 5
	done
	# Get ladder data; this is a single API call so we just do it with curl
    done;
done;

echo "Done with ladder data."



cd $data_dir

for BRACKET in ${BRACKETS[@]};
do
    for ZONE in ${ZONES[@]};
    do
	echo "Running $BRACKET $ZONE"
	# Convert to a more workable format
	python3 $code_dir/process_ladder_data.py \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_ladder.json \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_ladder.csv

	# The ladder data is missing a bunch of character-specific information (e.g. class)
	# so we need to fetch this with API calls


	# Get a list of all the names and realms for each person
	cat .tmp/${todays_date}_${ZONE}_${BRACKET}_ladder.json |jq .entries[] \
	    | jq '.character|{name, realm}' > .tmp/${ZONE}_${BRACKET}_ladder_chars.json

	# Get name and server for each person on the ladder
	cat .tmp/${ZONE}_${BRACKET}_ladder_chars.json \
	    | jq .name > .tmp/${ZONE}_${BRACKET}_char_name
	
	cat .tmp/${ZONE}_${BRACKET}_ladder_chars.json \
	    | jq .realm | jq .slug > .tmp/${ZONE}_${BRACKET}_char_realm

	# Glue together into a single file; prep for API calls
	paste .tmp/${ZONE}_${BRACKET}_char_name .tmp/${ZONE}_${BRACKET}_char_realm -d ',' \
	      > .tmp/${ZONE}_${BRACKET}_names_realms


	# Run requests against Blizzard API to get character data for those
	# on the ladder
	python3 $code_dir/get_api_character_requests.py \
		.tmp/${ZONE}_${BRACKET}_names_realms \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char.json \
		${ZONE} $token
	
	# Process character data; convert json to CSV
	python3 $code_dir/process_character_data.py \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char.json \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char.csv

	python3 $code_dir/get_api_pvp_requests.py \
		.tmp/${ZONE}_${BRACKET}_names_realms \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_pvp.json \
		${ZONE} $token

	python3 $code_dir/process_pvp_character_data.py \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_pvp.json \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_pvp.csv
	

	python3 $code_dir/join_character_and_pvp_data.py \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char.csv \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_pvp.csv \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char_pvp.csv
	
	# Join ladder data and character data together
	python3 $code_dir/join_datasets_on_key.py \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_ladder.csv \
		.tmp/${todays_date}_${ZONE}_${BRACKET}_char_pvp.csv \
		id \
		${todays_date}_${ZONE}_${BRACKET}_leaderboard.csv

    done;
done;
