
To install ROOT Distributedly:

```ssh -XY jboulis@lxplus.cern.ch``` (if you are outside CERN network)

**To access CERN hpc-batch cluster:**
```ssh -XY jboulis@hpc-batch.cern.ch```

OR

**To access JURECA in jülich:**
```ssh -i ~/.ssh/id_ed25519 boulis1@judac.fz-juelich.de``` (to any login node without IPv4)
```ssh -i ~/.ssh/id_ed25519 boulis1@jureca-ipv4.fz-juelich.de``` (to any login node with IPv4)
```ssh -i ~/.ssh/id_ed25519 username@jurecaXX.fz-juelich.de``` (to access a specific login node without IPv4)
```ssh -4 -i ~/.ssh/id_ed25519 username@jurecaXX.fz-juelich.de``` (to access a specific login node with IPv4)

mkdir rootproject_s && cd rootproject_s/
curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/launch_build.py
curl -O https://raw.githubusercontent.com/josephhany/Distributed-Benchmarking/main/launch_build.sh
git clone https://github.com/root-project/root.git root_src
git clone https://github.com/siliataider/root.git root_src
chmod u+x launch_build.sh
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && chmod +x Miniconda*.sh && ./Miniconda*.sh (remember to install it where the project is see next slide) && echo 'export PATH="$PATH:$CONDA_PREFIX/bin"' >> ~/.bashrc && source ~/.bashrc
conda install -n base -c conda-forge mamba
mamba create -n rootdev numpy pytest dask distributed dask-jobqueue matplotlib screen ninja
srun -p photon --time=24:00:0 -N 1 -c 32 --tasks-per-node=1 --pty bash -i
conda activate rootdev
screen -S experiment1
./launch_build.sh rootdev distrdf-release
Ctrl + A + D
screen -r experiment1
```
