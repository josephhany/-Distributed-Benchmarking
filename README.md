
# Install ROOT Distributedly

In order to install ROOT, you will need to have access to the internet to download some necessary packages. However, in most HPCs, the only nodes that have access to the internet are the login nodes. Thus, we are going to install ROOT on the shared storage system from the login nodes. However, the following installation will not work if the login nodes have a different operating system or architecture than the worker nodes. In this case, please follow the instructions in section ().

To check whether the login node has the same architecture and operating system as the worker nodes, execute the following command on a login node and worker node and compare the OS and Arch:

```
cat /etc/os-release

uname -m
```

**To access a worker node, execute the following command:**

For JURECA:
```
srun -p dc-cpu -A slfse --time=1:00:0 -N 1 -c 64 --tasks-per-node=1 --pty bash -i
```

For hpc-batch:
```
srun -p photon --time=1:00:0 -N 1 -c 32 --tasks-per-node=1 --pty bash -i
```

**Usage:**

`-p` is the queue name which is `dc-cpu` for `JURECA` and `photon` for `hpc-batch`

`-A` is the budget account which is `slfse` for `JURECA` and none for `hpc-batch`

`--time` is wall-clock time. The less it is the faster the allocation. In the above command, we specify it to be 1 hour `1:00:00`

`-N` is the Number of nodes allocated which is 1 in the above commands

`-c` is the Number of cores per node which is `64` for JURECA and `32` for `hpc-batch`


**Note:** Replace `jboulis` and `boulis1` in the following commands with your username for lxplus, hpc-batch, juelich

(1) Access the desired cluster

```
ssh -XY jboulis@lxplus.cern.ch
```

To access CERN hpc-batch cluster:

```
ssh -XY jboulis@hpc-batch.cern.ch
```

OR

To access JURECA in jülich:

```
ssh -i ~/.ssh/id_ed25519 boulis1@judac.fz-juelich.de # to access any login node without IPv4

ssh -i ~/.ssh/id_ed25519 boulis1@jureca-ipv4.fz-juelich.de # to access any login node with IPv4

ssh -i ~/.ssh/id_ed25519 username@jurecaXX.fz-juelich.de # to access a specific login node without IPv4

ssh -4 -i ~/.ssh/id_ed25519 username@jurecaXX.fz-juelich.de # to access a specific login node with IPv4
```

Now, you should be logged in the desired HPC

(2) Download the installation scripts and setup the configuration

Execute this command if you are using JURECA,
```
cd /p/home/jusers/$(whoami)
```

```
mkdir rootproject && cd rootproject/

curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/Install-ROOT/launch_build.py

curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/Install-ROOT/launch_build.sh

git clone https://github.com/root-project/root.git root_src

chmod u+x launch_build.sh
```

(3) Install Mamba (ref)[https://root-forum.cern.ch/t/root-build-with-python-3-7-in-centos7/53162/7?u=vpadulan]

The bash script will install mamba into a folder of your choice. For simplicity, in the following, I suppose you installed it in a folder called `mambaforge` in the same directory where you ran the bash script.

```
cd /p/project/cslfse/$(whoami)

curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"

bash Mambaforge-$(uname)-$(uname -m).sh

source mambaforge/bin/activate
```

(4) Create and activate a new environment with the required libraries

```
mamba create -n rootdev numpy pytest dask distributed dask-jobqueue matplotlib screen ninja
```

# In case of having Arch or OS mismatch between login nodes and worker nodes

```
srun -p photon --time=24:00:0 -N 1 -c 32 --tasks-per-node=1 --pty bash -i
```

```
conda activate rootdev
```

(5) Start the installation of ROOT on a separate Screen

```
screen -S experiment1

./launch_build.sh rootdev distrdf-release

Ctrl + A + D

screen -r experiment1
```

# Install Prometheus and Exporters

**If you're using JURECA, execute the following command before starting installation:**

```
mkdir /p/project/cslfse/$(whoami) && cd /p/project/cslfse/$(whoami)
```

**To install Prometheus:**
```
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvf prometheus-2.46.0.linux-amd64.tar.gz

mv prometheus-2.46.0.linux-amd64/ prometheus/

cd prometheus/

./prometheus --config.file=prometheus.yml
```

**To install Node Exporter**
(link)[https://prometheus.io/docs/guides/node-exporter/]

**To install Slurm Exporter**
(link)[]

# Running Benchmarks

# Modifying environment variables

Environment Variable to disable caching

```
echo 'export EXTRA_CLING_ARGS="-O2"' >> ~/.bashrc
```

**Source .bashrc to **

```
source ~/.bashrc
```

To find project name in JURECA, either get it from JuDoor portal or execute this commands:
```
find /p/project/ -maxdepth 1 -type d -exec test -r {} \; -print | awk -F/ '!/\/\./ && !/\/(test|ddn-ime|project$)/ {print $NF}'
```

# Getting Data into Julich


# PromQL queries to query Prometheus time-series database

This query calculates the per-second rate of change (instantaneous rate) in the "node_network_receive_bytes_total" metric over a 30-second window
```
irate(node_network_receive_bytes_total[30s])
```

This query calculates the rate of change of the process_cpu_seconds_total metric over a 30-second time window and then multiplies the result by 100 to get CPU utilization in percentage
```
rate(process_cpu_seconds_total[30s]) * 100
```
