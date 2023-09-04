#!/bin/bash

cores=128
#cores=4096

nfiles=500

#nfiles=16000
ncores_per_node=128
LOGS_DIR=logs
benchmark_name="df102_NanoAODDimuonAnalysis"
cluster_name="Julich"
max_num_of_cores=2048

mkdir -p $LOGS_DIR

# Record the start time
start_time=$(date '+%Y-%m-%d %H:%M:%S')

screen -dmS prometheus /bin/bash -c "cd /p/project/cslfse/boulis1/prometheus && ./prometheus --web.enable-lifecycle --config.file=prometheus.yml"
screen -S prometheus-slurm-exporter -dm bash -c "cd /p/project/cslfse/boulis1/prometheus-slurm-exporter && ./bin/prometheus-slurm-exporter"
screen -S grafana -dm bash -c "cd /p/project/cslfse/boulis1/grafana-10.0.3/bin/ && ./grafana-server"

data_size=$((nfiles * 2))
echo "Running Benchmark $benchmark_name on $cluster_name with cores from $cores to $max_num_of_cores with data from $data_size MB to $((data_size * 32)) MB" >> "runtimes_df102_release_1.csv"

while [[ $cores -le $max_num_of_cores ]] # 2048, 4096
do
        # Set parameters
        nnodes=$(printf "%.0f" $(echo "($cores + $ncores_per_node - 1) / $ncores_per_node" | bc))

        if [ "$cores" -ge "$ncores_per_node" ]
        then
                ncores_per_task=$ncores_per_node
        else
                ncores_per_task=$cores
        fi

        # Debugging: Output information before starting each screen session
        echo "Spawning screen with $cores cores, $nnodes nodes, and $ncores_per_task cores per task."

        # Launch the Python script in a screen session with a specific name
        # screen -dmS with_$cores python $1 -c $ncores_per_task -N $nnodes
        # screen -dmS with_$cores bash -c "source ~/.bashrc && python $1 -c $ncores_per_task -N $nnodes"

        python df102_NanoAODDimuonAnalysis_4.py -c $ncores_per_task -N $nnodes -nf $nfiles -nt 3
        #screen -dmS with_$cores bash -c "python $1 -c $ncores_per_task -N $nnodes > logs/log_$cores.txt 2>&1"
        cores=$(( cores * 2 )) # Double the cores for the next iteration

        nfiles=$(( nfiles * 2))
done

# Record the end time
end_time=$(date '+%Y-%m-%d %H:%M:%S')

# Calculate the total time taken
total_time=$(date -u -d "$(date -d "$end_time" '+%s') - $(date -d "$start_time" '+%s')" '+%H:%M:%S')

# Append the time information to the CSV file
echo "Start Time,End Time,Total Time" >> "runtimes_df102_release_1.csv"
echo "$start_time,$end_time,$total_time" >> "runtimes_df102_release_1.csv"
