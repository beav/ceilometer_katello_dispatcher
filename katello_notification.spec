%global use_systemd (0%{?fedora} && 0%{?fedora} >= 17) || (0%{?rhel} && 0%{?rhel} >= 7)
Name: katello_notification
Version: 0.0.11
Release: 1%{?dist}

Summary: A daemon to read events off of the openstack messagebus and feed into katello
Group: Development/Libraries
License: GPLv2
Source0: %{name}-%{version}.tar.gz
URL: http://github.com/Katello/katello_notification
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

%if %use_systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%endif

Requires: katello-cli-common
Requires: python-ceilometer >= 2013.2

BuildRequires: python-setuptools
%if %use_systemd
# We need the systemd RPM macros
BuildRequires: systemd
%endif

%description
A daemon to read events off of the openstack messagebus and feed into katello

%prep
%setup -q -n katello_notification-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}
%if %use_systemd
    install -d -m 755 %{buildroot}/%{_unitdir}
    install -m 644 %{name}.service %{buildroot}/%{_unitdir}/%{name}.service
%else
    install -D bin/openstack-katello-notification %{buildroot}/etc/rc.d/init.d/openstack-katello-notification
%endif
install -D bin/katello-notification %{buildroot}/usr/bin/katello-notification
install -D etc/katello-notification.conf %{buildroot}/etc/katello/katello-notification.conf
install -d -m 755 %{buildroot}/%{_var}/log/%{name}

%post
%if %use_systemd
    %systemd_post %{name}.service
%else
    /sbin/chkconfig --add openstack-katello-notification
%endif

%preun
%if %use_systemd
    %systemd_preun %{name}.service
%else
    if [ $1 -eq 0 ] ; then
        /sbin/service openstack-katello-notification stop >/dev/null 2>&1
        /sbin/chkconfig --del openstack-katello-notification
    fi
%endif

%postun
%if %use_systemd
    %systemd_postun_with_restart %{name}.service
%else
    if [ "$1" -ge "1" ] ; then
        /sbin/service openstack-katello-notification condrestart >/dev/null 2>&1 || :
    fi
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.md

%dir %{python_sitelib}/katello_notification
%{python_sitelib}/katello_notification/*
%{python_sitelib}/katello_notification-*.egg-info
%attr(755,root,root) %{_bindir}/katello-notification
%if %use_systemd
    %attr(644,root,root) %{_unitdir}/%{name}.service
%else
    %attr(755,root,root) %{_initrddir}/openstack-katello-notification
%endif
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/katello/katello-notification.conf
%attr(755,ceilometer,root) %dir %{_var}/log/%{name}




%changelog
* Tue Apr 08 2014 Chris Duryee <cduryee@redhat.com> 0.0.11-1
- 1081868: better error message when systems are not found (cduryee@redhat.com)
- allow setting log level via conf file (cduryee@redhat.com)

* Thu Mar 27 2014 Chris Duryee <cduryee@redhat.com> 0.0.10-1
- rewrite to use oslo.messaging libs (cduryee@redhat.com)
- initialize a new connection per-use (cduryee@redhat.com)
- use correct init.d script name (cduryee@redhat.com)
- systemd support (cduryee@redhat.com)

* Sat Mar 15 2014 Chris Duryee <cduryee@redhat.com> 0.0.9-1
- hack for registration race condition, and convert str to int
  (cduryee@redhat.com)
- use profile name instead of hostname (cduryee@redhat.com)
- autoregistration of spacewalk hypervisors (cduryee@redhat.com)
- support autoregistration of hypervisors (cduryee@redhat.com)
- pull list of guests from SW before pushing new guest (cduryee@redhat.com)

* Sun Mar 09 2014 Chris Duryee <cduryee@redhat.com> 0.0.8-1
- clean up logging a bit (cduryee@redhat.com)
- remove consumer cache (cduryee@redhat.com)
- logging cleanup, and look for message state for deletes (cduryee@redhat.com)
- handle "exists" messages (cduryee@redhat.com)
- initial spacewalk support (cduryee@redhat.com)
- use conf file instead of hardcoded katello (cduryee@redhat.com)
- pep8 fixups (cduryee@redhat.com)
- big refactor (cduryee@redhat.com)

* Tue Jan 14 2014 Chris Duryee <cduryee@redhat.com> 0.0.7-1
- fix spec typo (cduryee@redhat.com)

* Tue Jan 14 2014 Chris Duryee <cduryee@redhat.com> 0.0.6-1
- new package built with tito

* Fri Nov 08 2013 Chris Duryee <cduryee@redhat.com> 0.0.5-1
- refactor to not use python-rhsm (cduryee@redhat.com)
- nosetests (cduryee@redhat.com)
- travis stuff (cduryee@redhat.com)
- add stylish tests (cduryee@redhat.com)
- fix logging (cduryee@redhat.com)

* Wed Nov 06 2013 Chris Duryee <cduryee@redhat.com> 0.0.4-1
- spec file fixup (cduryee@redhat.com)

* Wed Nov 06 2013 Chris Duryee <cduryee@redhat.com> 0.0.3-1
- spec file fixup (cduryee@redhat.com)
- spec file fixup (cduryee@redhat.com)
- spec file fixup (cduryee@redhat.com)

