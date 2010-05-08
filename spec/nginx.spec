%define nginx_user      nginx
%define nginx_group     %{nginx_user}
%define nginx_home      %{_localstatedir}/lib/nginx
%define nginx_home_tmp  %{nginx_home}/tmp
%define nginx_logdir    %{_localstatedir}/log/nginx
%define nginx_confdir   %{_sysconfdir}/nginx
%define nginx_datadir   %{_datadir}/nginx
%define nginx_webroot   %{nginx_datadir}/html

Name:           nginx
Version:        0.7.64
Release:        2%{?dist}
Summary:        Fast Rails web serving.
Group:          System Environment/Daemons

License:        BSD
URL:            http://nginx.org/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)

BuildRequires:      ruby-devel,rubygems,git,pcre-devel,zlib-devel,openssl-devel
Requires:           pcre,zlib,openssl
Requires:           perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
# for /usr/sbin/useradd
Requires(pre):      shadow-utils
Requires(post):     chkconfig
# for /sbin/service
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts

Source0:    http://nginx.org/download/nginx-%{version}.tar.gz
Source1:    %{name}.init
Source2:    %{name}.conf

%description
Nginx [engine x] is an HTTP(S) server, HTTP(S) reverse proxy and IMAP/POP3
proxy server written by Igor Sysoev. Passenger was made by Phusion and helps
us serve Rails apps with Nginx.

%prep
%setup

%build
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
cp -R * $RPM_BUILD_ROOT/

%install
find $RPM_BUILD_ROOT -type f -exec chmod 0644 {} \;
chmod 0755 $RPM_BUILD_ROOT%{_sbindir}/%{name}
%{__install} -p -D -m 0755 %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/%{name}
%{__install} -p -D -m 0755 %{SOURCE2} $RPM_BUILD_ROOT%{nginx_confdir}/%{name}.conf
%{__install} -p -d -m 0755 $RPM_BUILD_ROOT%{nginx_confdir}/conf.d
%{__install} -p -d -m 0755 $RPM_BUILD_ROOT%{nginx_datadir}
%{__install} -p -d -m 0755 $RPM_BUILD_ROOT%{nginx_home_tmp}
%{__install} -p -d -m 0755 $RPM_BUILD_ROOT%{nginx_logdir}
%{__install} -p -d -m 0755 $RPM_BUILD_ROOT%{nginx_webroot}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ $1 == 1 ]; then
    %{_sbindir}/useradd -c "Nginx user" -s /bin/false -r -d %{nginx_home} %{nginx_user} 2>/dev/null || :
fi

%post
if [ $1 == 1 ]; then
    /sbin/chkconfig --add %{name}
fi

%preun
if [ $1 = 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
if [ $1 == 2 ]; then
    /sbin/service %{name} upgrade || :
fi

%files
%defattr(-,root,root,-)
%{nginx_datadir}/
%{nginx_home_tmp}/
%{nginx_webroot}/
%{_sbindir}/%{name}
%{_initrddir}/%{name}
%dir %{nginx_confdir}
%dir %{nginx_logdir}
%config(noreplace) %{nginx_confdir}/%{name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}


%changelog
* Mon May 03 2010 Brad Fults <brad at causes dot com> - 0.7.64-2
- Forked from the original 'nginx' package
- Added passenger recompilation

* Fri Dec 04 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.64-1
- Update to new stable 0.7.64

* Tue Oct 29 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.63-1
- Update to new stable 0.7.63
- reinstate zlib dependency

* Mon Sep 14 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.62-1
- Update to new stable 0.7.62
- fixes CVE-2009-2629
- fix rpmlint zlib dependency complaint

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 0.7.61-2
- rebuilt with new openssl

* Sun Aug 02 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.7.61-1
- Update to new stable 0.7.61

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.36-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun May 17 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.36-2
- init script updates from Gena Makhomed
- remove nginx-upstream-fair

* Sat Apr 11 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.36-1
-  update to 0.6.36

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.35-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Feb 19 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.35-2
- rebuild

* Thu Feb 19 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.35-1
- update to 0.6.35

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 0.6.34-2
- rebuild with new openssl

* Tue Dec 30 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.34-1
- update to 0.6.34

* Thu Dec  4 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.6.33-2
- Fix inclusion of /usr/share/nginx tree => no unowned directories.

* Sun Nov 23 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.33-1
- update to 0.6.33

* Tue Jul 22 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.32-1
- update to 0.6.32
- nginx now supports DESTDIR so removed the patches that enabled it

* Mon May 26 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.31-3
- init script fixes
- resolve 'listen 80 default' [#447873]

* Mon May 12 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.31-2
- update to 0.6.31

* Sun May 11 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.30-2
- upate to new upstream stable branch 0.6
- added 3rd party module nginx-upstream-fair
- added default webpages

* Sun Apr 20 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.5.35-2
- update init script to match recommended guidelines
- add /etc/nginx/conf.d support [#443280]
- use /etc/sysconfig/nginx to determine nginx.conf [#442708]

* Tue Mar 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.5.35-3
- add Requires for versioned perl (libperl.so)
- drop silly file Requires

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.5.35-2
- Autorebuild for GCC 4.3

* Sat Jan 19 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.5.35-1
- update to 0.5.35

* Sat Dec 15 2007 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.5.34-1
- update to 0.5.34

* Wed Dec 05 2007 Release Engineering <rel-eng at fedoraproject dot org> - 0.5.33-2
 - Rebuild for deps

* Sun Nov 11 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.33-1
- update to 0.5.33

* Mon Sep 24 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.32-1
- updated to 0.5.32
- fixed rpmlint UTF-8 complaints.

* Sat Aug 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.31-2
- added --with-http_stub_status_module build option.
- added --with-http_sub_module build option.
- added use of pcre-config --cflags

* Fri Aug 17 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.31-1
- Update to 0.5.31
- specify license is BSD

* Sat Aug 11 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.30-2
- Add BuildRequires: perl-devel - fixing rawhide build

* Mon Jul 30 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.30-1
- Update to 0.5.30

* Tue Jul 24 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.29-1
- Update to 0.5.29

* Wed Jul 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.28-1
- Update to 0.5.28

* Mon Jul 09 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.27-1
- Update to 0.5.27

* Mon Jun 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.26-1
- Update to 0.5.26

* Sat Apr 28 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.19-1
- Update to 0.5.19

* Mon Apr 02 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.17-1
- Update to 0.5.17

* Mon Mar 26 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.16-1
- Update to 0.5.16
- add ownership of /usr/share/nginx/html (#233950)

* Fri Mar 23 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-3
- fixed package review bugs (#235222) given by ruben@rubenkerkhof.com

* Thu Mar 22 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-2
- fixed package review bugs (#233522) given by kevin@tummy.com

* Thu Mar 22 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-1
- create patches to assist with building for Fedora
- initial packaging for Fedora
