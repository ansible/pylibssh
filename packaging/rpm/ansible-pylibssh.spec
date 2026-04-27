%global pypi_name ansible-pylibssh

# NOTE: The target version may be set dynamically via
# NOTE: rpmbuild --define "upstream_version 0.2.1.dev125+g0b5bde0"
%global upstream_version_fallback %(ls -t dist/%{pypi_name}-*.tar.gz 2>/dev/null | head -n 1 | sed 's#^dist\\/%{pypi_name}-\\(.*\\)\\.tar\\.gz$#\\1#')
# If "upstream_version" macro is unset, use the fallback defined above:
%if "%{!?upstream_version:UNSET}" == "UNSET"
%global upstream_version %{upstream_version_fallback}
%endif

%global python_importable_name pylibsshext

%global buildroot_site_packages "%{buildroot}%{python3_sitearch}"

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
# Prevent requiring a Build ID in the compiled shared objects
%global debug_package   %{nil}
%endif

# NOTE: Newer distro versions enable the source_date_epoch_from_changelog macro
# NOTE: and it breaks because we don't currently include the change log.
# Ref: https://fedoraproject.org/wiki/Changes/ReproducibleBuildsClampMtimes
%global source_date_epoch_from_changelog 0

Name:    python-%{pypi_name}
Version: %{upstream_version}
Release: 1%{?dist}
Summary: Python bindings for libssh client specific to Ansible use case

#BuildRoot: %%{_tmppath}/%%{name}-%%{version}-%%{release}-buildroot
License: LGPL-2+
URL:     https://github.com/ansible/pylibssh
Source0: %{pypi_source}

# `pyproject-rpm-macros` provides %%pyproject_buildrequires
BuildRequires: pyproject-rpm-macros

# Test dependencies:
# keygen?
BuildRequires: openssh
# sshd?
BuildRequires: openssh-server
# ssh?
BuildRequires: openssh-clients

# Build dependencies:
BuildRequires: gcc

BuildRequires: libssh-devel
BuildRequires: python3-devel


# Runtime dependencies:
Requires: libssh >= 0.9.0

%description
$summary


# Stolen from https://src.fedoraproject.org/rpms/python-pep517/blob/rawhide/f/python-pep517.spec#_25
%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
$summary

%prep
%autosetup -p1 -n %{pypi_name}-%{version}

%if 0%{?rhel} == 9
# NOTE: Since RHEL 9 does not have setuptools-scm 7+ in the repos, we change the
# NOTE: metadata to require a lower version and hope for the best
sed -i 's/\(.*"setuptools-scm\)[^"]\+\(",.*\)/\1 >= 6\2/g' pyproject.toml
%endif

%generate_buildrequires
%pyproject_buildrequires -t


%build

%pyproject_wheel


%install

%pyproject_install
%pyproject_save_files "%{python_importable_name}"


%check

export PYTHONPATH="%{buildroot_site_packages}:${PYTHONPATH}"
%pyproject_check_import
%tox -e just-pytest


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE.rst
%doc README.rst


%changelog
