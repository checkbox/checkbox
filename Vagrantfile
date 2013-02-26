# -*- mode: ruby -*-
# vi: set ft=ruby sw=2 ts=2 :

Vagrant::Config.run do |config|

  # Define a Ubuntu Server image (cloud) for the 12.10 release (quantal)
  config.vm.define :quantal do |quantal_config|
    quantal_config.vm.box = "quantal-cloud-i386"
    quantal_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/quantal/current/quantal-server-cloudimg-i386-vagrant-disk1.box"
  end

  # Define a Ubuntu Server image (cloud) for the 12.04 release (precise)
  config.vm.define :precise do |precise_config|
    precise_config.vm.box = "precise-cloud-i386"
    precise_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"
  end

  # For debugging and later future GUI testing
  # config.vm.boot_mode = :gui

  # Update to have the latest packages, this is needed because the image comes
  # with an old (and no longer working) apt cache and links to many packages no
  # longer work.
  config.vm.provision :shell, :inline => "apt-get update && apt-get dist-upgrade --yes"
  # Install dependencies from native packages
  config.vm.provision :shell, :inline => "apt-get install --yes python3-setuptools python3-yaml python3-lxml"
  # Install python3-mock so that we can create mock objects for testing
  config.vm.provision :shell, :inline => "apt-get install --yes python3-mock"
  # Install policykit-1 so that we have pkexec
  config.vm.provision :shell, :inline => "apt-get install --yes policykit-1"
  # Install some checkbox script dependencies:
  # Later on those could be installed on demand to test how we behave without
  # them but for now that's good enough. Little by little...
  config.vm.provision :shell, :inline => "apt-get install --yes fwts"
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
  # Create a cool symlink so that everyone knows where to go to
  config.vm.provision :shell, :inline => "ln -fs /vagrant /home/vagrant/checkbox"
end
