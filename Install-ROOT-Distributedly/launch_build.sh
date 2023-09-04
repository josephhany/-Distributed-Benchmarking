#!/bin/sh

# input to the script
# $1 conda environment name
# $2 root building mode

# This line re-executes this same script in a clean environment
# created via the env -i command. The `CLEANED` env var is set
# so that it doesn't lead to an infinite re-execution
[ -z "$CLEANED" ] && exec /bin/env -i CLEANED=1 /bin/sh "$0" "$@"

# Activate conda
eval "$(/hpcscratch/user/jboulis/mambaforge/bin/conda shell.bash hook)"
conda activate $1

# GCC
source /cvmfs/sft.cern.ch/lcg/contrib/gcc/13/x86_64-centos7/setup.sh
# CMAKE
export PATH=/cvmfs/sft.cern.ch/lcg/contrib/CMake/3.26.2/Linux-x86_64/bin/:$PATH
# Ninja
export PATH=/cvmfs/sft.cern.ch/lcg/contrib/ninja/1.11.1/Linux-x86_64/bin/:$PATH
# Git
export PATH=/cvmfs/sft.cern.ch/lcg/contrib/git/2.28.0/x86_64-centos7/bin/:$PATH

#############################################################
####### Asking the user for cleaning previous builds ########
#############################################################

# Prompt the user whether to remove previous builds
read -p "Do you want to remove previous builds? (y/n): " remove_builds

if [[ $remove_builds =~ ^[Yy]$ ]]; then
  # Remove the 'root_build/' directory
  if [ -d "root_build/" ]; then
    rm -r root_build/
    echo "Previous builds removed."
  else
    echo "No previous builds found."
  fi
fi

#############################################################
####### Launching the root build with the right mode ########
#############################################################

python launch_build.py --mode $2

###############################################
####### sourcing the right thisroot.sh ########
###############################################

# Pattern for matching the directories
pattern="root_install/master-*-$1-$2"

# Prompt the user for a specific directory name
read -p "Do you have a specific directory name where '/bin/thisroot.sh' exists? (y/n): " has_specific_dir

if [[ $has_specific_dir =~ ^[Yy]$ ]]; then
  read -p "Enter the specific directory name where '/bin/thisroot.sh' exists: " specific_dir_name
  thisroot_file="root_install/$specific_dir_name/bin/thisroot.sh"

  if [ -f "$thisroot_file" ]; then
    echo "Sourcing $thisroot_file"
    source "$thisroot_file"
  else
    echo "Error: 'thisroot.sh' not found in $specific_dir_name/bin/"
  fi
else
  # Find the last created directory matching the pattern
  last_directory=$(ls -td $pattern 2>/dev/null | head -n 1)

  if [ -n "$last_directory" ]; then
    # Check if 'thisroot.sh' exists inside the 'bin/' folder of the last created directory
    thisroot_file="$last_directory/bin/thisroot.sh"

    if [ -f "$thisroot_file" ]; then
      echo "Sourcing $thisroot_file"
      source "$thisroot_file"
    else
      echo "Error: 'thisroot.sh' not found in $last_directory/bin/"
    fi
  else
    echo "No directories found matching the pattern '$pattern'"
  fi
fi
