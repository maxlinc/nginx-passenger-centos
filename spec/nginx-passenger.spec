%define nginx_name      nginx
%define nginx_version   1.2.6
%define nginx_user      nginx
%define nginx_group     %{nginx_user}
%define nginx_home      %{_localstatedir}/lib/nginx
%define nginx_home_tmp  %{nginx_home}/tmp
%define nginx_logdir    %{_localstatedir}/log/nginx
%define nginx_confdir   %{_sysconfdir}/nginx
%define nginx_datadir   %{_datadir}/nginx
%define nginx_webroot   %{nginx_datadir}/html
%define passenger_version   3.0.19
# This should match `passenger-config --root`
%define passenger_dir   %{_libdir}/passenger-%{passenger_version}

Name:           nginx-passenger
Version:        %{nginx_version}+%{passenger_version}
Release:        2%{?dist}
Summary:        Robust, small and high performance http and reverse proxy server
Group:          System Environment/Daemons

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:        BSD
URL:            http://nginx.net/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)

BuildRequires:      pcre-devel,zlib-devel,openssl-devel
Requires:           pcre,zlib,openssl
# for /usr/sbin/useradd
Requires(pre):      shadow-utils
Requires(post):     chkconfig
# for /sbin/service
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts

Source0:    http://nginx.org/download/nginx-%{nginx_version}.tar.gz
Source1:    %{nginx_name}.init
Source2:    %{nginx_name}.conf

Patch0:     nginx-install-sbin.patch

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev.

%prep
%setup -q -n %{nginx_name}-%{nginx_version}

%patch0 -p1

%{__cat} <<EOF >%{nginx_name}.logrotate
%{nginx_logdir}/*log {
    daily
    rotate 10
    missingok
    notifempty
    compress
    sharedscripts
    postrotate
        [ ! -f /var/run/nginx.pid ] || kill -USR1 `cat %{_localstatedir}/run/%{nginx_name}.pid`
    endscript
}
EOF

%{__cat} <<EOF >%{nginx_name}.sysconfig
# Configuration file for the %{nginx_name} service

# set this to the location of the %{nginx_name} configuration file
NGINX_CONF_FILE=%{nginx_confdir}/%{nginx_name}.conf
EOF


%build
# compile support for nginx in passenger
MY_BUILD_DIR=`pwd`
cd `passenger-config --root`
rake nginx
mkdir -p $MY_BUILD_DIR/%{passenger_dir}
cp -r . $MY_BUILD_DIR/%{passenger_dir}
cd $MY_BUILD_DIR

# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.  The configure script(s) have been patched (Patch1 and
# Patch2) in order to support installing into a build environment.
export DESTDIR=%{buildroot}
./configure \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/%{nginx_name} \
    --conf-path=%{nginx_confdir}/%{nginx_name}.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --pid-path=%{_localstatedir}/run/%{nginx_name}.pid \
    --lock-path=%{_localstatedir}/lock/subsys/%{nginx_name} \
    --with-http_ssl_module \
    --with-http_gzip_static_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-ipv6 \
    --add-module=`passenger-config --root`/ext/nginx
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor
find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{nginx_name}
%{__install} -p -D -m 0755 %{SOURCE2} %{buildroot}%{nginx_confdir}
%{__install} -p -D -m 0644 %{nginx_name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{nginx_name}
%{__install} -p -D -m 0644 %{nginx_name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{nginx_name}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_logdir}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_webroot}
%{__install} -p -m 0644 html/50x.html %{buildroot}%{nginx_webroot}
%{__install} -p -m 0644 html/index.html %{buildroot}%{nginx_webroot}
%{__install} -p -d -m 0755 %{buildroot}/%{passenger_dir}
cp -a `pwd`/%{passenger_dir} %{buildroot}/%{passenger_dir}

# convert to UTF-8 all files that give warnings.
for textfile in CHANGES
do
    mv $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    rm -f $textfile.old
done

%clean
rm -rf %{buildroot}

%pre
if [ $1 == 1 ]; then
    %{_sbindir}/useradd -c "Nginx user" -s /bin/false -r -d %{nginx_home} %{nginx_user} 2>/dev/null || :
fi

%post
if [ $1 == 1 ]; then
    /sbin/chkconfig --add %{nginx_name}
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{nginx_name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{nginx_name}
fi

%postun
if [ $1 == 2 ]; then
    /sbin/service %{nginx_name} upgrade || :
fi

%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README
%{nginx_datadir}/
%{passenger_dir}/
%{_sbindir}/%{nginx_name}
%{_initrddir}/%{nginx_name}
%dir %{nginx_confdir}
%dir %{nginx_confdir}/conf.d
%dir %{nginx_logdir}
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{nginx_name}.conf.default
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/%{nginx_name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{_sysconfdir}/logrotate.d/%{nginx_name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{nginx_name}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
