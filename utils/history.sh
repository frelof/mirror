file="../data/temperature.json"
( echo 'timestamp,temperature_c,humidity_percent'
  git log --follow --format='%H' --reverse -- "$file" \
  | while read -r sha; do git show "$sha:$file" | jq -r '[.timestamp,.temperature_c,.humidity_percent]|@csv'; done
) > readings.csv
