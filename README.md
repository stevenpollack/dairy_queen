[![Binder](http://mybinder.org/badge.svg)](http://mybinder.org/repo/stevenpollack/dairy_queen)

# dairy_queen

This repository contains python code to calculate all possible "double dips" for
a specified set of show times, according to specified parameters.

A double dip (really, an _n_ dip) is just a fancy (non-technical) term to mean
a sequence of movies. You may know this by another term, but if you've ever
gone to the movies and seen two films in sequence, you've double dipped.

Now, extend this to _n_ films, back-to-back, and you've just completed an
n-dip...

# Installation and Usage
There's a vagrant box (ubuntu 14.04 64-bit) provisioned to test everything
out on. The provisioning is rather basic:

1. install `git`, and `vim`
2. install `rethinkdb` and set it up to start as a service
3. install `python` via miniconda

The python step is a bit weighty -- it'll cost however much miniconda weighs
as well as an addition 95 MB (for jupyter, pandas, and requests).

Once you've booted up the vagrant machine:
```bash
cd /path/to/dairy_queen
vagrant up
```
you can access the `rethinkdb` dashboard via
http://localhost:1880/ or you can work in an `jupyter` notebook via
http://localhost:1888/

Of course you can always get into the vagrant box via
```bash
vagrant ssh
```

Should you want to use vim in all of its pre-configured glory, you'll
have to run the install procedure from _inside the vagrant box_:
```bash
vim -e +PluginInstall +VimProcInstall +qall now
```
