#!/bin/bash

if [ -d "ostis" ]; 
	then
		echo -en "Update OSTIS platform\n"
		cd ostis
		git pull
		cd ../
	else
		echo -en "Install OSTIS platform\n"
		git clone https://github.com/ShunkevichDV/ostis.git
		echo "../kb" >> ostis/repo.path
fi

cd ostis/scripts
./prepare.sh
