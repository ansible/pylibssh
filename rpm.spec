# Running this should be enough to build an SRPM and a binary RPM:
# dnf install -y dnf-plugins-core rpm-build rpmdevtools rpmlint && \
#   rpmdev-setuptree && \
#   cd ~/rpmbuild/SOURCES && \
#   curl -O https://files.pythonhosted.org/packages/20/15/5d0abfbb294034d049f7777dbcc1638e634b13dcff7687063ac8350d95a1/ansible-pylibssh-0.2.0.tar.gz && \
#   curl -O https://files.pythonhosted.org/packages/a4/8f/67123c5c9e63a658dffdd073c0b95a4d96e2152d1d9ffee754022360d4e1/expandvars-0.7.0.tar.gz && \
#   cd /io && \
#   rpmlint rpm.spec && \
#   rpmbuild -bs rpm.spec && \
#   dnf builddep -y /root/rpmbuild/SRPMS/python-ansible-pylibssh-0.2.0-1.fc34.src.rpm && \
#   rpmbuild -bb rpm.spec

# FIXME: figure out why using `python3dist(...)` syntax does not work

%global pypi_name ansible-pylibssh
%global python_importable_name pylibsshext
 
Name:    python-%{pypi_name}
#Version: 0.2.1.dev78
Version: 0.2.0
Release: 1%{?dist}
Summary: Python bindings for libssh client specific to Ansible use case

License: LGPL-2+
URL:     https://github.com/ansible/pylibssh
#Source0: .
Source0: https://files.pythonhosted.org/packages/20/15/5d0abfbb294034d049f7777dbcc1638e634b13dcff7687063ac8350d95a1/ansible-pylibssh-0.2.0.tar.gz
Source1: https://files.pythonhosted.org/packages/a4/8f/67123c5c9e63a658dffdd073c0b95a4d96e2152d1d9ffee754022360d4e1/expandvars-0.7.0.tar.gz

BuildRequires: gcc

BuildRequires: libssh-devel
BuildRequires: python3-devel

#BuildRequires: python3-Cython  # coming from %%pyproject_buildrequires
# `python3-toml` is not retrieved by %%pyproject_buildrequires for some reason
BuildRequires: python3-toml

#BuildRequires: python3dist(cython)
##BuildRequires: python3dist(expandvars)
#BuildRequires: python3dist(packaging)
#BuildRequires: python3dist(pip) >= 19
#BuildRequires: python3dist(setuptools) >= 45
#BuildRequires: python3dist(setuptools-scm) >= 3.5
#BuildRequires: python3dist(setuptools-scm-git-archive) >= 1.1
#BuildRequires: python3dist(setuptools-scm[toml]) >= 3.5
#BuildRequires: python3dist(toml)
#BuildRequires: python3dist(wheel)

# `pyproject-rpm-macros` provides %%pyproject_buildrequires
BuildRequires: pyproject-rpm-macros

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
%autosetup -n %{pypi_name}-%{version}

sed -i '/"expandvars",/d' pyproject.toml

python -m pip install --no-deps -t bin %{SOURCE1}

%generate_buildrequires
%pyproject_buildrequires


%build

%pyproject_wheel %{python_importable_name}


%install
%pyproject_install
%pyproject_save_files "%{python_importable_name}"


%check


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE.rst
%doc README.rst


%changelog

