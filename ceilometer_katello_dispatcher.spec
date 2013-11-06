Name: ceilometer_katello_dispatcher
Version: 0.0.3
Release: 1%{?dist}

Summary: A ceilometer dispatcher to feed instance events into katello
Group: Development/Libraries
License: GPLv2
Source0: %{name}-%{version}.tar.gz
URL: http://github.com/Katello/ceilometer_katello_dispatcher
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: python-rhsm >= 1.8.9

BuildRequires: python-setuptools

%description
A ceilometer dispatcher to feed instance events into katello

%prep
%setup -q -n ceilometer_katello_dispatcher-%{version}

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

%dir %{python_sitelib}/ceilometer_katello_dispatcher

%{python_sitelib}/ceilometer_katello_dispatcher/*
%{python_sitelib}/ceilometer_katello_dispatcher-*.egg-info

%changelog
* Wed Nov 06 2013 Chris Duryee <cduryee@redhat.com> 0.0.3-1
- spec file fixup (cduryee@redhat.com)
- spec file fixup (cduryee@redhat.com)
- spec file fixup (cduryee@redhat.com)

