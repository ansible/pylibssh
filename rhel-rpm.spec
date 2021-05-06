# Running this should be enough to build an SRPM and a binary RPM:
# rpm -i https://rpmfind.net/linux/centos/8-stream/AppStream/x86_64/os/Packages/cmake-filesystem-3.18.2-9.el8.x86_64.rpm https://rpmfind.net/linux/centos/8-stream/AppStream/x86_64/os/Packages/libssh-devel-0.9.4-2.el8.x86_64.rpm &&
# dnf install epel-release && \
#   dnf install -y dnf-plugins-core rpm-build && \
#   mkdir -pv ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS} && \
#   cd /io && \
#   rpmbuild --undefine=_disable_source_fetch -bs rhel-rpm.spec && \
#   dnf builddep -y /root/rpmbuild/SRPMS/python-ansible-pylibssh-0.2.0-1.el8.src.rpm && \
#   rpmbuild -bb rhel-rpm.spec

%global pypi_name ansible-pylibssh
%global normalized_dist_name ansible_pylibssh
%global python_importable_name pylibsshext
%global whl_glob %{normalized_dist_name}-%{version}-cp3*-cp3*-linux_%{_arch}.whl
 
Name:    python-%{pypi_name}
Version: 0.2.0
Release: 1%{?dist}
Summary: Python bindings for libssh client specific to Ansible use case

License: LGPL-2+
URL:     https://github.com/ansible/pylibssh
Source0: %{pypi_source}
Source1: %{pypi_source expandvars 0.7.0}
Source2: %{pypi_source build 0.3.1.post1}
Source3: %{pypi_source Cython 0.29.23}
Source4: %{pypi_source packaging 20.9}
Source5: %{pypi_source setuptools 56.0.0}
Source6: %{pypi_source setuptools_scm 6.0.1}
Source7: %{pypi_source setuptools_scm_git_archive 1.1}
Source8: %{pypi_source toml 0.10.2}
Source9: %{pypi_source pep517 0.10.0}
Source10: %{pypi_source pip 21.1.1}
Source11: %{pypi_source pyparsing 2.4.7}
Source12: %{pypi_source importlib_metadata 4.0.1}
Source13: %{pypi_source zipp 3.4.1}
Source14: %{pypi_source typing_extensions 3.10.0.0}

BuildRequires: gcc

BuildRequires: libssh-devel
BuildRequires: python3-devel

BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)

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

%{__python3} -m pip install --no-deps -t bin %{SOURCE1}
%{__python3} -m pip install --no-deps -t bin %{SOURCE9}
%{__python3} -m pip install --no-deps -t bin %{SOURCE2}
%{__python3} -m pip install --no-deps -t bin %{SOURCE10}
%{__python3} -m pip install --no-deps -t bin  %{SOURCE3} --install-option="--no-cython-compile"
%{__python3} -m pip install --no-deps -t bin %{SOURCE4}
%{__python3} -m pip install --no-deps -t bin %{SOURCE5}
PYTHONPATH=bin/ %{__python3} -m pip install --no-deps -t bin %{SOURCE6}
%{__python3} -m pip install --no-deps -t bin %{SOURCE7}
%{__python3} -m pip install --no-deps -t bin %{SOURCE8}
%{__python3} -m pip install --no-deps -t bin %{SOURCE11}
PYTHONPATH=bin/ %{__python3} -m pip install --no-deps -t bin %{SOURCE12}
PYTHONPATH=bin/ %{__python3} -m pip install --no-deps -t bin %{SOURCE13}
%{__python3} -m pip install --no-deps -t bin %{SOURCE14}

%build

PYTHONPATH=bin/ \
%{__python3} \
  -m build \
  --wheel \
  --skip-dependencies \
  --no-isolation \
  .


%install
%{py3_install_wheel %{whl_glob}}


%check


%files -n python3-%{pypi_name}
%license LICENSE.rst
%doc README.rst
# NOTE: %%{python3_sitelib} points to /lib/ while %%{python3_sitearch}
# NOTE: points to /lib64/ when necessary.
%{python3_sitearch}/%{python_importable_name}
%{python3_sitearch}/%{normalized_dist_name}-%{version}.dist-info

%changelog

