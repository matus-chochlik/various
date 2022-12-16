#!/bin/bash
for png in *.png
do convert ${png} -resize 50% ${png%.png}-50p.png && mv ${png%.png}-50p.png ${png} && echo ${png}
done
