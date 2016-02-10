#!/bin/bash

# install anaconda and jupyter (as a service)
miniconda=/vagrant/provisioning/Miniconda3-latest-Linux-x86_64.sh
anaconda_dir=/opt/anaconda
anaconda_bin=$anaconda_dir/bin
jupyter_initd=/vagrant/provisioning/init.d_jupyter-notebook
jupyter_config=/vagrant/config_files/jupyter_notebook_config.py

cd /vagrant

if [[ ! -f $miniconda ]]; then
  wget --quiet http://repo.continuum.io/miniconda/$miniconda
fi

chmod +x $miniconda
$miniconda -b -p $anaconda_dir

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

# if we don't turn off MKL there's 212.6 MB of packages to download;
# otherwise theres ~ 95 MB
conda install -y nomkl
conda install -y jupyter pandas requests

# copy over config file to default location
mkdir /home/vagrant/.jupyter
sudo ln -fs $jupyter_config /home/vagrant/.jupyter/jupyter_notebook_config.py

# setup jupyter service init.d 
if [[ ! -f $jupyter_initd ]]; then
  wget -O $jupyter_initd https://gist.githubusercontent.com/stevenpollack/bcd54262313352cebdbd/raw/init.d_jupyter-notebook
fi

sudo chmod +x $jupyter_initd
sudo ln -fs $jupyter_initd /etc/init.d/jupyter-notebook

sudo /etc/init.d/jupyter-notebook restart

