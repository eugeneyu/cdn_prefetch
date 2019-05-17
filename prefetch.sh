#!/bin/bash
# Update the project id, private key file, known_hosts file
# Execution: prefetch.sh http://sample.com/file

PROJECT=youzhi-lab
KEY=~/.ssh/prefetch_key
KNOWN_HOSTS=~/.ssh/known_hosts
# FETCH_URL=http://34.96.65.189/do_not_delete/test.txt

FETCH_URL=$1

declare -a arr=('asia-east1-a' 'asia-east2-a' 'asia-northeast1-a' 'asia-northeast2-a' 'asia-south1-a'
                'asia-southeast1-a' 'australia-southeast1-a' 'europe-north1-a' 'europe-west1-b'
                'europe-west2-a' 'europe-west3-a' 'europe-west4-a' 'northamerica-northeast1-a'
                'southamerica-east1-a' 'us-central1-a' 'us-east1-b' 'us-east4-a' 'us-west1-a' 'us-west2-a'
                )

echo '' > result.log


for i in "${arr[@]}"
do
	ZONE_FROM=$i
	ZONE_AVG_RESULT=($ZONE_FROM)
	SERVER_FROM=cdn-prefetch-$ZONE_FROM.$ZONE_FROM.c.$PROJECT.internal
	ssh-keygen -f $KNOWN_HOSTS -R $SERVER_FROM
	RESULTS=$(ssh -oStrictHostKeyChecking=no -i $KEY prefetch@$SERVER_FROM curl $FETCH_URL -o download 2>&1 )
	echo $SERVER_FROM fetch result $RESULTS >> result.log
done
echo 'done!'