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

## Download & Extract Nginx

    cd /tmp
    wget http://nginx.org/download/nginx-0.7.64.tar.gz
    tar -xzf nginx-0.7.64.tar.gz

## Get Necessary System-specific Configs

    git clone git://github.com/causes/nginx-passenger-centos.git
    cp nginx-passenger-centos/init/nginx.init ~/rpmbuild/SOURCES/
    cp nginx-passenger-centos/conf/nginx.conf ~/rpmbuild/SOURCES/
    cp nginx-passenger-centos/spec/nginx.spec ~/rpmbuild/SPECS/

## Rebuild Nginx with Passenger Module
    mkdir /tmp/nginx-build && cd /tmp/nginx-build
    passenger-install-nginx-module --auto \
      --nginx-source-dir=/tmp/nginx-0.7.64 \
      --prefix=/tmp/nginx-build \
      --extra-configure-flags="--user=nginx --group=nginx --with-http_ssl_module --with-http_gzip_static_module --with-http_random_index_module --with-ipv6"

## Create RPM File Structure
    mkdir -p nginx-0.7.64 nginx-0.7.64/usr/share/nginx nginx-0.7.64/etc/nginx
    mv html nginx-0.7.64/usr/share/nginx/
    mv conf/mime.types nginx-0.7.64/etc/nginx/
    mv sbin nginx-0.7.64/usr/
    find . -maxdepth 1 -mindepth 1 -not -name nginx-0.7.64 -exec rm -rf {} \;
    tar -czf nginx-0.7.64.tar.gz nginx-0.7.64/
    mv -f nginx-0.7.64.tar.gz ~/rpmbuild/SOURCES/

## Build the RPM
    cd ~/rpmbuild/
    rpm -ba SPECS/nginx.spec

The resulting RPM will be:

    ~/rpmbuild/RPMS/x86_64/nginx-0.7.64-2.x86_64.rpm
