Name: katello_notification
Version: 0.0.7
Release: 1%{?dist}

Summary: A daemon to read events off of the openstack messagebus and feed into katello
Group: Development/Libraries
License: GPLv2
Source0: %{name}-%{version}.tar.gz
URL: http://github.com/Katello/katello_notification
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# needs to be version after uuid merge
Requires: katello-cli-common
Requires: python-ceilometer >= 2013.2

BuildRequires: python-setuptools

%description
A daemon to read events off of the openstack messagebus and feed into katello

%prep
%setup -q -n katello_notification-%{version}

%build
%{__python} setup.py build

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --root %{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.md

%dir %{python_sitelib}/katello_notification

%{python_sitelib}/katello_notification/*
%{python_sitelib}/katello_notification-*.egg-info

%changelog
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

