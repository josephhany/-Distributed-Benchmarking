import argparse
import os
import re
import shlex
import subprocess

ROOT_HOME = os.path.join(os.getcwd(), "root_src")
ROOT_BUILD = os.path.join(os.getcwd(), "root_build")
if not os.path.exists(ROOT_BUILD):
    os.mkdir(ROOT_BUILD)
ROOT_INSTALL = os.path.join(os.getcwd(), "root_install")
if not os.path.exists(ROOT_INSTALL):
    os.mkdir(ROOT_INSTALL)

build_opts = {
    "default":"-DCMAKE_BUILD_TYPE=RelWithDebInfo",
    "debug":"-DCMAKE_BUILD_TYPE=Debug",
    "release":"-DCMAKE_BUILD_TYPE=Release",
    "testing":"-DCMAKE_BUILD_TYPE=Debug -Dtesting=ON -Droottest=ON",
    "distrdf-debug":(
        "-Dminimal=ON -Dpyroot=ON "
        "-Ddataframe=ON -Dxrootd=ON -Dtest_distrdf_pyspark=ON -Dtest_distrdf_dask=ON "
        "-DCMAKE_BUILD_TYPE=Debug -Dimt=ON "
        "-Dgminimal=ON -Dasimage=ON "
    ),
    "distrdf-release":"-Dminimal=ON -Dpyroot=ON -Ddataframe=ON -Dxrootd=ON -DCMAKE_BUILD_TYPE=Release -Dgminimal=ON -Dasimage=ON",
    "distrdf-rel-with-deb-info":"-Dminimal=ON -Dpyroot=ON -Ddataframe=ON -Dxrootd=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo -Dgminimal=ON -Dasimage=ON",
    "minimal":"-Dminimal=ON -Ddev=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo",
    "cling-profile-debug":"-DCMAKE_BUILD_TYPE=Debug -DLLVM_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS_DEBUG='-O0 -g -fno-omit-frame-pointer'",
    "cling-profile-relwithdebinfo":(
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo -DLLVM_BUILD_TYPE=RelWithDebInfo "
        "-DCMAKE_CXX_FLAGS_RELWITHDEBINFO='-O2 -g -fno-omit-frame-pointer' "
        "-Dminimal=ON -Dpyroot=ON -Ddataframe=ON -Dxrootd=ON -Dimt=ON"
    ),
    "pyroot-debug":"-Dminimal=ON -Dpyroot=ON -DCMAKE_BUILD_TYPE=Debug",
}

parser = argparse.ArgumentParser()
parser.add_argument("--njobs", help="As in 'cmake -jNJOBS'", type=int)
parser.add_argument("--name", help="The name of this build")
parser.add_argument("--mode", help="Build process mode", choices=list(build_opts.keys()), default="default")
parser.add_argument("--opts", help="List of cmake options", action="append", nargs=argparse.REMAINDER)
args = parser.parse_args()

def launch_build():
    if args.name is None:
        p = subprocess.run(["git","status"], cwd=ROOT_HOME, check=True, capture_output=True)
        gitstatus = p.stdout.decode()
        pattern = re.compile("^On branch (?P<branch>.*)")
        branch = pattern.match(gitstatus).groupdict()["branch"]

        if branch == "master":
            # Further specify builds on the master branch with the commit SHA
            p = subprocess.run(["git","rev-parse", "--short", "HEAD"], cwd=ROOT_HOME, check=True, capture_output=True)
            sha = p.stdout.decode().rstrip()
            branch += "-" + sha

        dirname = branch + "-" + args.mode if args.mode else branch + "-custom"
    else:
        dirname = args.name if args.name else dirname
    # Check if we are using a conda environment
    dirname = dirname + (f"-conda-{os.environ['CONDA_DEFAULT_ENV']}" if os.environ.get('CONDA_DEFAULT_ENV', "") else "")
    
    build_dir = os.path.join(ROOT_BUILD, dirname)
    if not os.path.exists(build_dir):
        os.mkdir(build_dir)
    install_dir = os.path.join(ROOT_INSTALL, dirname)
    if not os.path.exists(install_dir):
        os.mkdir(install_dir)

    if not os.path.exists(os.path.join(build_dir, "CMakeCache.txt")):
        base_opts = shlex.split("cmake")
        mode_opts = shlex.split(build_opts[args.mode]) if args.mode else args.opts[0]
        dirs_opts = shlex.split(f"-DCMAKE_INSTALL_PREFIX={install_dir} -B {build_dir} -S {ROOT_HOME}")
        configure_command = base_opts + mode_opts + dirs_opts
        subprocess.run(configure_command, check=True)

    njobs = args.njobs if args.njobs else os.cpu_count()
    build_command = f"cmake --build {build_dir} --target install -j{njobs}"
    subprocess.run(shlex.split(build_command), check=True)

if __name__ == "__main__":
    launch_build()
