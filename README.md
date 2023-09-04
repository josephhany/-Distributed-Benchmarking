
**To install ROOT Distributedly:**

In order to install ROOT, you will need to have access to the internet to download some necessary packages. However, in most HPCs, the only nodes that have access to the internet are the login nodes. Thus, we are going to install ROOT on the shared storage system from the login nodes. However, the following installation will not work if the login nodes have different operating system or architecture than the worker nodes. In this case, please follow the instructions in section ().

To check whether the login node has the same architecture and operating system as the worker nodes, execute the following command on a login node:

```
cat /etc/os-release
```

**Note:** Replace jboulis and boulis1 in the following commands with your username for lxplus, hpc-batch, juelich

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

Now, you should be inside the desired HPC

(2) Download the installation scripts and setup the configuration

Execute this command if you are using JURECA,
```
mkdir /p/project/cslfse/$(whoami) && cd /p/project/cslfse/$(whoami)
```

```
mkdir rootproject && cd rootproject/

curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/Install-ROOT/launch_build.py

curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/Install-ROOT/launch_build.sh

git clone https://github.com/root-project/root.git root_src

chmod u+x launch_build.sh
```

(3) Install Miniconda and Mamba

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && chmod +x Miniconda*.sh && ./Miniconda*.sh (remember to install it where the project is see next slide) && echo 'export PATH="$PATH:$CONDA_PREFIX/bin"' >> ~/.bashrc && source ~/.bashrc

conda install -n base -c conda-forge mamba
```

(4) Create and activate a new environment with the required libraries

```
mamba create -n rootdev numpy pytest dask distributed dask-jobqueue matplotlib screen ninja

srun -p photon --time=24:00:0 -N 1 -c 32 --tasks-per-node=1 --pty bash -i

conda activate rootdev
```

(5) Start the installation of ROOT on a separate Screen

```
screen -S experiment1

./launch_build.sh rootdev distrdf-release

Ctrl + A + D

screen -r experiment1
```

**To install Prometheus:**
```
wget https://github.com/prometheus/prometheus/releases/download/v2.46.0/prometheus-2.46.0.linux-amd64.tar.gz
tar -xvf prometheus-2.46.0.linux-amd64.tar.gz

mv prometheus-2.46.0.linux-amd64/ prometheus/

cd prometheus/

./prometheus --config.file=prometheus.yml
```
