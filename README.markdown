# A Recipe for an Nginx + Passenger RPM on CentOS

A simplified/revised version of swhitt's [centos-apache-passenger][cap], which
is similar to jnstq's [rails-nginx-passenger-ubuntu][rnpu] recipe but for
Nginx + Passenger on CentOS. Also influenced by the deploy scripts used by
EngineYard Solo.

  [cap]: http://github.com/swhitt/centos-apache-passenger
  [rnpu]: http://github.com/jnstq/rails-nginx-passenger-ubuntu

Perform the following on a build box as root.

## Create an RPM Build Environment
    yum install rpmdevtools
    rpmdev-setuptree

## Install Prerequisites for Nginx + Passenger RPM Creation
    yum groupinstall 'Development Tools'
    yum install ruby-devel openssl-devel zlib-devel pcre-devel rubygems git
    gem install passenger -v 2.2.11

Hereafter, this process assumes that `passenger-config --root` returns a
usable value for the location of Passenger's installed files. The RPM will
build nginx-specific extensions for Passenger (by running `rake nginx` in
Passenger's main directory) and will compile against the module in Passenger's
`ext/nginx/` directory.

Passenger's `ext/nginx/HelperServer` file is dynamically linked and must be
present at runtime for the nginx integration to work correctly.

## Download Nginx
    cd ~/rpmbuild
    curl http://nginx.org/download/nginx-0.7.65.tar.gz -o SOURCES/nginx-0.7.65.tar.gz

## Get Necessary System-specific Configs
    cd /tmp
    git clone git://github.com/causes/nginx-passenger-centos.git
    cp nginx-passenger-centos/init/nginx.init ~/rpmbuild/SOURCES/
    cp nginx-passenger-centos/conf/nginx.conf ~/rpmbuild/SOURCES/
    cp nginx-passenger-centos/spec/nginx.spec ~/rpmbuild/SPECS/

## Build the RPM
    cd ~/rpmbuild/
    rpmbuild -ba SPECS/nginx-passenger.spec

The resulting RPM will be:

    ~/rpmbuild/RPMS/x86_64/nginx-passenger-0.7.65+2.2.11-2.x86_64.rpm
