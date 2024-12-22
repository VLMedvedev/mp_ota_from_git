#!/bin/sh

file_name="text-16.pf";
#file_name="configured.html";

printf "blob $(wc -c < "$file_name")\0$(cat "$file_name")" | sha1sum

exit 0
