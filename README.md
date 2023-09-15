
# Install ROOT Distributedly

In order to install ROOT, you will need to have access to the internet to download some necessary packages. However, in most HPCs, the only nodes that have access to the internet are the login nodes. Thus, we are going to install ROOT on the shared storage system from the login nodes. It is also important to note that the following installation will not work if the login nodes have a different operating system or architecture than the worker nodes. In this case, please follow the instructions in section ().

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

(3) Install Mamba [ref](https://root-forum.cern.ch/t/root-build-with-python-3-7-in-centos7/53162/7?u=vpadulan)

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

**To run prometheus:**

```
screen -dmS prometheus /bin/bash -c "cd /p/project/cslfse/boulis1/prometheus && ./prometheus --web.enable-lifecycle --config.file=prometheus.yml"
```

Replace `/p/project/cslfse/boulis1/prometheus` with your prometheus installation directory path.

**To install Node Exporter**
(link)[https://prometheus.io/docs/guides/node-exporter/]

**To install Slurm Exporter**
(link)[]

# Modifying environment variables

Environment Variable to disable caching

```
echo 'export EXTRA_CLING_ARGS="-O2"' >> ~/.bashrc
```

**Source .bashrc to **

```
source ~/.bashrc
```

# To enable/disable AsyncPrefetching

```
vim $ROOTSYS/etc/system.rootrc
```
Search for `TFile.AsyncPrefetching` and make it `yes` to enable AsyncPrefetching or `no` to disable it.

[link](https://root-forum.cern.ch/t/enable-async-prefetching-per-file-per-tree/25504)

vim $ROOTSYS/etc/system.rootrc

To find project name in JURECA, either get it from JuDoor portal or execute this commands:
```
find /p/project/ -maxdepth 1 -type d -exec test -r {} \; -print | awk -F/ '!/\/\./ && !/\/(test|ddn-ime|project$)/ {print $NF}'
```

# Uploading your SSH key to Julich



# Getting Data into Julich

Since Julich does not allow users to use `xrdcp` to copy data files locally from `root://eospublic.cern.ch//eos/opendata/`, you have to use `scp` utility to copy `.root` files from storage connected to CERN network. However, you need to make sure to have the same private key that you were using inside of lxplus (note: normal user's lxplus storage was not sufficient to hold data).

One solution is to download the data on hpc-batch (photon partition) and use `scp` to send it to JURECA.

First, we need to have the same private key located on hpc-batch.

Second, we need to make the private key readable and writable only by its owner while denying any access to group members and others.

```
chmod 600 /hpcscratch/user/jboulis/data/id_ed25519
```

Then, we can use `scp` normally to copy the data from hpc-batch to JURECA

```
scp -i /hpcscratch/user/jboulis/data/id_ed25519 /hpcscratch/user/jboulis/data/Run2012BC_DoubleMuParked_Muons.root boulis1@jureca-ipv4.fz-juelich.de:/p/project/cslfse/boulis1/data/
```

# Getting Data from Julich

After geeting `id_ed25519` private key and executing `chmod 600` on it, execute the following command on your local machine to get data from JURECA.

**Note**: To include the jump host (intermediate host) directly in the scp command, we use the `-o` option to specify a `ProxyJump` configuration. This allows you to use the scp command as if you were copying files directly from your local machine to the remote host, with the intermediate host acting as a jump host in the middle.

```
scp -i ~/Downloads/id_ed25519 -o ProxyJump=jboulis@lxplus.cern.ch boulis1@jureca-ipv4.fz-juelich.de:/p/home/jusers/boulis1/shared/rootproject/Distributed-Benchmarking/Jülich-jureca/Benchmarking-Data/data.tar.gz /home/jboulis/Downloads
```

# Running Benchmarks

Now, after you have installed ROOT, prometheus, node exporter, dask, and slurm exporter. You can run any benchmark by submitting it as job from any login node.

First, you need to make sure that you modify these variables in +++ file based on your HPC and environment.

```
QUEUE_NAME = 'dc-cpu' # queue name
LOGS_DIR = "logs" # 
DaskDashboardPort = 1243
LOCAL_DIRECTORY = '/tmp'
PROMETHEUS_CONFIG_PATH = '/p/project/cslfse/boulis1/prometheus/prometheus.yml'
CREATE_SCREEN_COMMAND = "/p/project/cslfse/boulis1/run_screen_script.sh"
EXEC_SCRIPT_PATH = '/p/project/cslfse/boulis1/exec_df102.sh'
ACOUNT_NAME = 'slfse'
```

Killing all processes using port 9090 (i.e., Killing running instances of Prometheus in the background, assuming prometheus port is 9090)
```
lsof -i :9090 | awk 'NR!=1 {print $2}' | xargs -r kill -9
```

# Using Port Forwarding to see enpoints on our local machine

```
ssh -XY -L 9090:localhost:9090 jboulis@lxplus763.cern.ch
```

```
ssh -XY -i ~/.ssh/id_ed25519 -L 9090:localhost:9090 boulis1@jureca-ipv4.fz-juelich.de
```

```
ssh -XY -L 9090:localhost:9090 jboulis@hpc-batch.cern.ch
```

**Note**: without `-XY` option, you will not be able to see the webpages.

# PromQL queries to query Prometheus time-series database

This query calculates the per-second rate of change (instantaneous rate) in the "node_network_receive_bytes_total" metric over a 30-second window
```
irate(node_network_receive_bytes_total[30s])
```

This query calculates the rate of change of the process_cpu_seconds_total metric over a 30-second time window and then multiplies the result by 100 to get CPU utilization in percentage
```
rate(process_cpu_seconds_total[30s]) * 100
```

# Run Benchmarks

After running the benchmark successfully, you will get a file ++++ that has the data in this format: +++.

Copy this data and paste it in the Data variable in this Notebook: [link](https://colab.research.google.com/drive/1aWk-P3iDjdeKQMTO-IGzFMakZB9o75a2?usp=sharing)

# Previous Benchmarking Data on Jülich

In order to access previous benchmarks results that we have run on Jülich, you have to have prometheus already installed and replace 'data/' directory in prometheus installation directory with the data directory found in this [link](https://drive.google.com/drive/folders/1NcQWjTXtePesSGvc4elSM0Me5kb4lK6n?usp=sharing).

Now, you can access all the data experiments data from the time series databse of prometheus found in the data directory. Below you will find a list of the experiment setup, start time, end time, and other relevant data.

**Experiment details:**
Running Benchmark [df102_NanoAODDimuonAnalysis](https://root.cern/doc/master/df102__NanoAODDimuonAnalysis_8py.html) on [JURECA](https://www.fz-juelich.de/en/ias/jsc/systems/supercomputers/jureca) with cores ranging from 128 to 2048 and with data ranging from 1000 MB to 16000 MB (cold starts were dropped while plotting the above graph)

**Experiment timing:**

| Start Time          | End Time            | Total Time |
|---------------------|---------------------|------------|
| 2023-08-21 18:48:52 | 2023-08-21 19:53:14 | 1h4m22s    |


**Experiment results:**

| core count | runtime (sec) |
|------------|---------------|
| 128        | 151.44 (cold start) |
| 128        | 142.46 |
| 128        | 152.20 |
| 256        | 168.50 (cold start) |
| 256        | 151.13 |
| 256        | 151.67 |
| 512        | 162.07 (cold start) |
| 512        | 151.41 |
| 512        | 152.19 |
| 1024       | 163.71 (cold start) |
| 1024       | 152.94 |
| 1024       | 152.40 |
| 2048       | 167.77 (cold start) |
| 2048       | 154.20 |
| 2048       | 153.89 |

Results graphed:

![image](https://github.com/josephhany/Distributed-Benchmarking/assets/54475725/61bae709-607b-4318-a0d1-94210fb9e61b)


To query prometheus timeseries databse for this time interval and get simillar graphs like the one below:

![Screenshot from 2023-09-14 20-34-12](https://github.com/josephhany/Distributed-Benchmarking/assets/54475725/1276012b-82fb-442c-841e-12120b0616a1)

You have to set 

![Screenshot from 2023-09-14 20-37-41](https://github.com/josephhany/Distributed-Benchmarking/assets/54475725/6ea2c00e-06b1-4423-b655-0aa99808fbea)


![Screenshot from 2023-09-14 20-39-01](https://github.com/josephhany/Distributed-Benchmarking/assets/54475725/99504ca8-969c-42c7-9d77-b78fbf464d6d)


# Previous Benchmarking Data on CERN cluster (hpc-batch)

since Julich does not allow +++++++ you have to +++++

```
Running Benchmark df102_NanoAODDimuonAnalysis on HPC-Batch with cores from 64 to 128 with data from 1000 MB to 2000 MB (without Async Prefetching)
64,782.4957950115204
128,565.8549840450287
Start Time,End Time,Total Time
2023-08-22 01:37:24,2023-08-22 02:19:29,00:42:05
```

```
Running Benchmark df102_NanoAODDimuonAnalysis on HPC-Batch with cores from 64 to 128 with data from 1000 MB to 2000 MB (with Async Prefetching)
64,511.76918387413025
128,521.8195469379425
Start Time,End Time,Total Time
2023-08-22 02:55:34,2023-08-22 03:38:10,00:42:18
```



HPC-batch data [link](https://drive.google.com/drive/folders/1XNj8aN8niSb4Wswj9_Qbd9oG7-x6HaQL?usp=sharing)
