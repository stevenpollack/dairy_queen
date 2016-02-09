#!/bin/bash

# install anaconda
miniconda=Miniconda3-latest-Linux-x86_64.sh
anacoda_dir=/opt/anaconda
anaconda_bin=$anacoda_dir/bin

cd /vagrant

if [[ ! -f $miniconda ]]; then
  wget --quiet http://repo.continuum.io/miniconda/$miniconda
fi

chmod +x $miniconda
./$miniconda -b -p $anacoda_dir

cat >> /home/vagrant/.bashrc << END
# add for anaconda install
PATH=$anacoda_bin:\$PATH
END

# package dependencies -- make sure that pip and conda are found
# inside the anaconda installation directory:
$anaconda_bin/pip install --upgrade pip
$anaconda_bin/pip install rethinkdb
$anacoda_bin/conda install -y jupyter pandas requests
