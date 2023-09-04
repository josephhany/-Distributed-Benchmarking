#!/bin/bash

source ~/.bashrc

echo "ROOT Installation: " `which root.exe`
echo "Python executable: " `which python`

parsed_hostnames=`scontrol show hostnames $SLURM_JOB_NODELIST | tr '\n' ',' | sed 's/.$//'
echo $parsed_hostnames`
nprocs=$SLURM_CPUS_PER_TASK
npartitions_per_core=1
export ncores_total=$(( (SLURM_JOB_NUM_NODES-1) * SLURM_CPUS_PER_TASK ))
npartitions=$(( ncores_total * npartitions_per_core ))
nfiles=16000
ntests=3

#4000 - 3999

if [ ! -e "/tmp/Run2012BC_DoubleMuParked_Muons.root" ]; then cp /p/project/cslfse/boulis1/data/Run2012BC_DoubleMuParked_Muons.root /tmp; fi
for i in `seq 1 15999`; do ln -s /tmp/Run2012BC_DoubleMuParked_Muons.root "/tmp/Run2012BC_DoubleMuParked_Muons_${i}.root"; done

echo "Running $ntests tests with:"
echo "- Hosts: ${parsed_hostnames}"
echo "- nprocs: $nprocs"
echo "- nfiles: $nfiles"
echo "- npartitions (total): $npartitions"
echo "- ncores (total): $ncores_total"

screen -wipe

if ! screen -list | grep -q "node_exporter"; then
        screen -dmS node_exporter /bin/bash -c 'source /hpcscratch/user/jboulis/mambaforge/etc/profile.d/conda.sh && conda activate /hpcscratch/user/jboulis/mambaforge/envs/rootdev_1 && cd /hpcscratch/user/jboulis/nodeexporter/node_exporter-1.6.1.linux-amd64 && ./node_exporter'
else
        echo "Screen session 'node_exporter' already exists."
fi
