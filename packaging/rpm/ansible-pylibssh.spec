%global pypi_name ansible-pylibssh

# NOTE: The target version may be set dynamically via
# NOTE: rpmbuild --define "upstream_version 0.2.1.dev125+g0b5bde0"
%global upstream_version_fallback %(ls -t dist/%{pypi_name}-*.tar.gz | head -n 1 | sed 's#^dist\\/%{pypi_name}-\\(.*\\)\\.tar\\.gz$#\\1#')
# If "upstream_version" macro is unset, use the fallback defined above:
%if "%{!?upstream_version:UNSET}" == "UNSET"
%global upstream_version %{upstream_version_fallback}
%endif

%global python_importable_name pylibsshext
# RHEL or CentOS:
%if 0%{?rhel}
%global normalized_dist_name ansible_pylibssh
%global whl_glob %{normalized_dist_name}-%{version}-cp3*-cp3*-linux_%{_arch}.whl
%endif

%global buildroot_site_packages "%{buildroot}%{python3_sitearch}"

Name:    python-%{pypi_name}
Version: %{upstream_version}
Release: 1%{?dist}
Summary: Python bindings for libssh client specific to Ansible use case

#BuildRoot: %%{_tmppath}/%%{name}-%%{version}-%%{release}-buildroot
License: LGPL-2+
URL:     https://github.com/ansible/pylibssh
Source0: %{pypi_source}
Source1: %{pypi_source expandvars 0.7.0}
# RHEL or CentOS:
%if 0%{?rhel}
Source2: %{pypi_source build 0.3.1.post1}
Source3: %{pypi_source Cython 0.29.23}
Source4: %{pypi_source packaging 20.9}
Source5: %{pypi_source setuptools 56.0.0}
Source6: %{pypi_source setuptools_scm 6.0.1}
Source7: %{pypi_source setuptools_scm_git_archive 1.4}
Source8: %{pypi_source toml 0.10.2}
Source9: %{pypi_source pep517 0.10.0}
Source10: %{pypi_source pip 21.1.1}
Source11: %{pypi_source pyparsing 2.4.7}
# RHEL specifically, not CentOS:
%if 0%{?centos} == 0
Source12: %{pypi_source importlib_metadata 4.0.1}
Source13: %{pypi_source zipp 3.4.1}
Source14: %{pypi_source typing_extensions 3.10.0.0}
%endif
Source15: %{pypi_source pytest 6.2.4}
Source16: %{pypi_source pytest-cov 2.12.1}
Source17: %{pypi_source pytest-forked 1.3.0}
Source18: %{pypi_source pytest-xdist 2.3.0}
Source19: %{pypi_source iniconfig 1.1.1}
Source20: %{pypi_source attrs 20.3.0}
Source21: %{pypi_source pluggy 0.13.1}
Source22: %{pypi_source py 1.10.0}
Source23: %{pypi_source coverage 5.5}
%endif

# Test dependencies:
# keygen?
BuildRequires: openssh
# sshd?
BuildRequires: openssh-server
# RHEL or CentOS:
%if 0%{?rhel}
BuildRequires: python3dist(pytest)
BuildRequires: python3dist(pytest-cov)
BuildRequires: python3dist(pytest-forked)
BuildRequires: python3dist(pytest-xdist)
BuildRequires: python3dist(tox)
%endif

# Build dependencies:
BuildRequires: gcc

BuildRequires: libssh-devel
BuildRequires: python3-devel

# RHEL or CentOS:
%if 0%{?rhel}
BuildRequires: python3dist(pip)
BuildRequires: python3dist(wheel)
# CentOS, not RHEL:
%if 0%{?centos}
BuildRequires: python3dist(importlib-metadata)
%endif
%endif
# Fedora:
%if 0%{?fedora}
# `pyproject-rpm-macros` provides %%pyproject_buildrequires
BuildRequires: pyproject-rpm-macros

# `python3-pip` is used to install vendored build deps
BuildRequires: python3-pip

# `python3-toml` is not retrieved by %%pyproject_buildrequires for some reason
BuildRequires: python3-toml
%endif

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

# Fedora:
%if 0%{?fedora}
sed -i '/"expandvars",/d' pyproject.toml
%endif

PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE1}

# RHEL or CentOS:
%if 0%{?rhel}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE9}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE2}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE10}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin  %{SOURCE3} --install-option="--no-cython-compile"
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE4}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE5}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE6}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE7}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE8}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE11}
# RHEL specifically, not CentOS:
%if 0%{?centos} == 0
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE12}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE13}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE14}
%endif
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE15}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE16}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE17}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE18}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE19}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE20}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE21}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE22}
PYTHONPATH="$(pwd)/bin" \
%{__python3} -m pip install --no-deps -t bin %{SOURCE23}
%endif

# Fedora:
%if 0%{?fedora}
%generate_buildrequires
%pyproject_buildrequires -t
%endif


%build

# Fedora:
%if 0%{?fedora}
%pyproject_wheel %{python_importable_name}
%endif

# RHEL or CentOS:
%if 0%{?rhel}
PYTHONPATH="$(pwd)/bin" \
%{__python3} \
  -m build \
  --wheel \
  --skip-dependencies \
  --no-isolation \
  .
%endif


%install

# Fedora:
%if 0%{?fedora}
%pyproject_install
%pyproject_save_files "%{python_importable_name}"
%endif

# RHEL or CentOS:
%if 0%{?rhel}
%{py3_install_wheel %{whl_glob}}
# Set the installer to rpm so that pip knows not to manage this dist:
sed \
  -i 's/pip/rpm/' \
  %{buildroot_site_packages}/%{normalized_dist_name}-%{version}.dist-info/INSTALLER
%endif


%check

export PYTHONPATH="%{buildroot_site_packages}:${PYTHONPATH}"
# Fedora:
%if "%{?fedora:SET}" == "SET"
%tox -e just-pytest -- \
  -vv \
  --installpkg '%{_builddir}/%{pypi_name}-%{upstream_version}/pyproject-wheeldir/%{whl_glob}' \
  -- \
  --deselect tests/unit/scp_test.py::test_get \
  --deselect tests/unit/scp_test.py::test_put
# CentOS or RHEL:
%else
export PYTHONPATH="$(pwd)/bin:${PYTHONPATH}"
%{__python3} -m pytest \
  --no-cov \
  --deselect tests/unit/scp_test.py::test_get \
  --deselect tests/unit/scp_test.py::test_put
%endif


%files -n python3-%{pypi_name} %{?fedora:-f %{pyproject_files}}
%license LICENSE.rst
%doc README.rst

# RHEL or CentOS
%if 0%{?rhel}
# NOTE: %%{python3_sitelib} points to /lib/ while %%{python3_sitearch}
# NOTE: points to /lib64/ when necessary.
%{python3_sitearch}/%{python_importable_name}
%{python3_sitearch}/%{normalized_dist_name}-%{version}.dist-info
%endif

%changelog
