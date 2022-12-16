#!/bin/bash
for png in *.png
do pngquant --quality 60-90 ${png} && mv ${png%.png}-fs8.png ${png} && echo ${png}
done
