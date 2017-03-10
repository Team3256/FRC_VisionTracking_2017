#!/bin/bash
echo "playing $1"
if [[ $1 == *.avi ]]
then
	vlc --rate=0.15 $1
else 
	echo "Not an .avi file"
fi
echo "Done"

