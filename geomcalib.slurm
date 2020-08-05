#!/bin/bash -l
#SBATCH --account=lcls
#SBATCH --job-name=autosfx
#SBATCH --nodes=1
#SBATCH --constraint=knl
#SBATCH --time=00:15:00
#SBATCH --image=docker:slaclcls/lcls-py2:latest
#SBATCH --exclusive
#SBATCH --qos=debug


case "$1" in
	setup)
		shifter \
		autosfx $1 \
		--exp cxic0515 --run 79 --outDir ./
		;;
	powdersum)
		srun -n 12 -c 1 shifter \
		autosfx $1 \
		--exp cxic0515 --run 79 --noe 1000 --outDir ./
		;;
	centerfinder)
		shifter \
		autosfx $1 \
		--img ./r0079/cxic0515_0079_max_assem.npy --mask ./r0079/psanaMask.npy
		;;
	peakfinder)
		shifter \
		autosfx $1 \
		--exp cxic0515 --run 79 --noe 300 --outDir ./
		;;
	indexer)
		shifter \
		autosfx $1 \
		--exp cxic0515 --run 79 --pdb /reg/data/ana03/scratch/autosfx/strep.cell --distance " -2,0,2 " --outDir ./
		;;
	distoptimizer)
		shifter \
		autosfx $1 \
		--stream "./r0079/cxic0515_0079_indexer_*.stream"
		;;
	*)
		echo "Usage: $0 {setup|powdersum|centerfinder|peakfinder|indexer|distoptimizer}"
		exit 1
esac

