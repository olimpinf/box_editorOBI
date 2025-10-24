#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: need a file name as argument (the contest cms file)"
    exit -1
fi


FILE=$1
DIR="${FILE%%.*}"

echo "../../../bin/build_cms.py -u users.csv ${FILE}"
../../../bin/build_cms.py -u users.csv ${FILE}

#echo "cmsImportUser -A ${DIR}"
#cmsImportUser -A ${DIR}

echo "cmsImportContest --update-contest --import-tasks ${DIR}"
#cmsImportContest --update-contest --import-tasks ${DIR}
cmsImportContest --update-contest --update-tasks ${DIR}

./update_time_limits.py piramide
./update_time_limits.py tanque
./update_time_limits.py cameras

