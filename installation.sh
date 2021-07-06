#!/bin/sh
# function for installing dependencies
Venv_func (){
    pip3 install uncurl
    pip3 install rich
    pip3 install requests
}
# get current python interp
VERSION=`python3 --version | tr -s ' ' | cut -d ' ' -f 2`
VERSIONIN=(${VERSION//./ })
case ${VERSIONIN[0]} in
    3)
        echo "Python version satisfied"
    ;;    
    *)
        echo "Needed version of the python is not installed"
        brew install python3
    ;;    
esac    

