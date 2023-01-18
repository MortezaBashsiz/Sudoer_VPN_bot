#!/bin/bash  -
#===============================================================================
#
#          FILE: sync.sh
#
#         USAGE: ./sync.sh [arv|cf]
#
#   DESCRIPTION: 
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Morteza Bashsiz (mb), morteza.bashsiz@gmail.com
#  ORGANIZATION: Linux
#       CREATED: 01/17/2023 10:00:23 PM
#      REVISION:  ---
#===============================================================================

set -o nounset                                  # Treat unset variables as an error

arv_hosts=( ip1.ip1.ip1.ip1 ip2.ip2.ip2.ip2 )
arv_regex="gheychi"
cf_hosts=( ip3.ip3.ip3.ip3 ip4.ip4.ip4.ip4 )
cf_regex="schere"
hosts=()
regex="null"
base_dir="null"

if [[ "$1" == "arv" ]]
then 
	base_dir="./$1"
	hosts=("${arv_hosts[@]}")
	regex="$arv_regex"
elif [[ "$1" == "cf" ]]
then
	base_dir="./$1"
	hosts=("${cf_hosts[@]}")
	regex="$cf_regex"
else
	echo "invalid input"
	exit 0
fi

local_urls_dir="$base_dir/urls"
host_urls_dir="/opt/v2ray_urls"
db_file="/opt/bot/bot-dev.db"

for host in "${hosts[@]}"
do
	host_local_urls_dir="$local_urls_dir/$host"
	rm -fr "$host_local_urls_dir"
	mkdir -p "$host_local_urls_dir"
	rsync -avh "$host:$host_urls_dir" "$host_local_urls_dir"
done

sqlite3 "$db_file" -cmd "delete from user_url where url in (select user_url.url from user_url left join urls on user_url.url=urls.url where hostname like \"%$regex%\");" ".exit"
sqlite3 "$db_file" -cmd "delete from urls where hostname like \"%$regex%\";" ".exit"

for file in $(find "$local_urls_dir" -type f -iname "*.url") 
do
	echo "$file"
	host="$(awk -F '://' '{print $2}' "$file" | base64 -d | jq -r .host )"
	sed -i "s/$/;$host/" "$file"
	python3 /opt/bot/insert_urls.py "$file"
done


