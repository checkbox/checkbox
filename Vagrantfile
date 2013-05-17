# -*- mode: ruby -*-
# vi: set ft=ruby sw=2 ts=2 :

Vagrant::Config.run do |config|

  config.ssh.timeout = 60

  # Define a Ubuntu Server image (cloud) for the 12.04 release (precise)
  config.vm.define :precise do |precise_config|
    precise_config.vm.box = "precise-cloud-i386"
    precise_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"
  end

  # Define a Ubuntu Server image (cloud) for the 12.10 release (quantal)
  config.vm.define :quantal do |quantal_config|
    quantal_config.vm.box = "quantal-cloud-i386"
    quantal_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/quantal/current/quantal-server-cloudimg-i386-vagrant-disk1.box"
  end

  # Define a Ubuntu Server image (cloud) for the 13.04 release (raring)
  config.vm.define :raring do |raring_config|
    raring_config.vm.box = "raring-cloud-i386"
    raring_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current/raring-server-cloudimg-i386-vagrant-disk1.box"
  end

  # For debugging and later future GUI testing
  if ENV.key? "VAGRANT_GUI"
    config.vm.boot_mode = :gui
  end

  # Setup an apt cache if one is available
  if ENV.key? "VAGRANT_APT_CACHE"
    config.vm.provision :shell, :inline => "echo 'Acquire::http { Proxy \"#{ENV['VAGRANT_APT_CACHE']}\"; };' > /etc/apt/apt.conf"
  end

  # Update to have the latest packages, this is needed because the image comes
  # with an old (and no longer working) apt cache and links to many packages no
  # longer work.
  config.vm.provision :shell, :inline => "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade --yes"
  # Install dependencies from native packages
  config.vm.provision :shell, :inline => "apt-get install --yes python3-setuptools python3-pkg-resources python3-lxml"
  # Install python3-mock so that we can create mock objects for testing
  config.vm.provision :shell, :inline => "apt-get install --yes python3-mock"
  # Install python3-sphinx so that we can build documentation
  config.vm.provision :shell, :inline => "apt-get install --yes python3-sphinx"
  # Install policykit-1 so that we have pkexec
  config.vm.provision :shell, :inline => "apt-get install --yes policykit-1"
  # Install some checkbox script dependencies:
  # Later on those could be installed on demand to test how we behave without
  # them but for now that's good enough. Little by little...
  config.vm.provision :shell, :inline => "apt-get install --yes fwts"
  # Develop checkbox so that we have it in $PATH
  config.vm.provision :shell, :inline => "cd /vagrant/ && python3 setup.py develop"
  # Develop plainbox so that we have it in $PATH
  config.vm.provision :shell, :inline => "cd /vagrant/plainbox/ && python3 setup.py develop"
  # Develop checkbox-ng so that we have it in $PATH
  config.vm.provision :shell, :inline => "cd /vagrant/checkbox-ng/ && python3 setup.py develop"
  # Create a cool symlink so that everyone knows where to go to
  config.vm.provision :shell, :inline => "ln --no-dereference --force --symbolic /vagrant /home/vagrant/checkbox"
end
