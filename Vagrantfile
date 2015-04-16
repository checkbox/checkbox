# -*- mode: ruby -*-
# vi: set ft=ruby sw=2 ts=2 :
Vagrant.require_version ">= 1.7.2"
Vagrant.configure("2") do |config|

  config.vm.provider "virtualbox"

  # Define a Ubuntu Server image (cloud) for the 12.04 release (precise)
  config.vm.define :precise do |precise_config|
    precise_config.vm.box = "precise-cloud-i386"
    precise_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"
  end

  # Define a Ubuntu Server image (cloud) for the 14.04 release (trusty)
  config.vm.define :trusty do |trusty_config|
    trusty_config.vm.box = "trusty-cloud-i386"
    trusty_config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box"
  end

  # For debugging and later future GUI testing
  if ENV.key? "VAGRANT_GUI"
    config.vm.boot_mode = :gui
  end

  if ENV.key? "VAGRANT_APT_CACHE"
    # Setup an apt cache if one is available and explicitly configured
    config.vm.provision :shell, :inline => "echo 'Acquire::http { Proxy \"#{ENV['VAGRANT_APT_CACHE']}\"; };' > /etc/apt/apt.conf"
  elsif File.exists? "/etc/apt-cacher-ng"
    # If apt-cacher-ng is installed on this machine then just use it.
    require 'socket'
    guessed_address = Socket.ip_address_list.detect{|intf| !intf.ipv4_loopback?}
    if guessed_address
      config.vm.provision :shell, :inline => "echo 'Acquire::http { Proxy \"http://#{guessed_address.ip_address}:3142\"; };' > /etc/apt/apt.conf"
    end
  end

  # Provision everything using a standalone shell script
  config.vm.provision :shell, :path => "support/provision-testing-environment"
end
