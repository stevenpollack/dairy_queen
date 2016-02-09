#!/bin/bash

# install anaconda
miniconda=Miniconda3-latest-Linux-x86_64.sh
anaconda_dir=/opt/anaconda
anaconda_bin=$anaconda_dir/bin

cd /vagrant

if [[ ! -f $miniconda ]]; then
  wget --quiet http://repo.continuum.io/miniconda/$miniconda
fi

chmod +x $miniconda
./$miniconda -b -p $anaconda_dir

cat >> /home/vagrant/.bashrc << END
# add for anaconda install
PATH=$anaconda_bin:\$PATH
END

# update the path during provisioning
export PATH=$anaconda_bin:$PATH

# package dependencies -- make sure that pip and conda are found
# inside the anaconda installation directory:
pip install --upgrade pip
pip install rethinkdb
conda install -y nomkl # we don't need MKL
conda install -y jupyter pandas requests
