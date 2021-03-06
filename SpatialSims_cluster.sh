nReals=50
nBatches=100
nSubs=(40 60 80 100 120 140 160 180 200 220 240 260 280 300 320 340 360 380 400 420 440 460 480 500)

for nSub in ${nSubs[@]}; do

	i=1
	while [ "$i" -le "$nBatches" ]; do

		# Submit nBatches batches and get the ids for them
		fsl_sub -l log/ -N batch${i} bash ./SpatialSims.sh $nSub $nReals > /tmp/$$ && batchIDs=$(awk 'match($0,/[0-9]+/){print substr($0, RSTART, RLENGTH)}' /tmp/$$),$batchIDs
		i=$(($i + 1))

	done
	if [ "$batchIDs" == "" ] ; then
		echo "Batch jobs submission failed!"	
	fi

done