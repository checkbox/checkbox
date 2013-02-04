# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "quantal-cloud-amd64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/quantal/current/quantal-server-cloudimg-amd64-vagrant-disk1.box"

  # Update to have the latest packages
  # Commented out for now, we don't really need it
  # config.vm.provision :shell, :inline => "apt-get update && apt-get dist-upgrade"
  # Install dependencies from native packages
  config.vm.provision :shell, :inline => "apt-get install --yes python3-setuptools python3-yaml python3-lxml"
  # Install python3-dev so that we can build native bits of other dependencies later
  config.vm.provision :shell, :inline => "apt-get install --yes python3-dev"
  # Install PIP so that we can install the rest from source
  config.vm.provision :shell, :inline => "apt-get install --yes python-pip" 
  # Update distribute as the version from ubuntu is too old to install coverage
  config.vm.provision :shell, :inline => "pip install -U distribute"
  # Install coverage
  config.vm.provision :shell, :inline => "pip install -U coverage"
  # Develop plainbox so that we have it in $PATH
  config.vm.provision :shell, :inline => "cd /vagrant/plainbox/ && python3 setup.py develop"
end
