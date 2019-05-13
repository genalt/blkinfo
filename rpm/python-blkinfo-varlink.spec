%if 0%{?fedora} || 0%{?rhel} >= 8
%global build_py3   1
%endif

Name:           python-blkinfo-varlink
Version: 	30.1.2
Release:        1%{?dist}
Summary:        Python implementation of Varlink for blkinfo interface
License:        ASL 2.0
URL:            https://github.com/varlink/python-varlink
Source0:        https://github.com/varlink/python-varlink/archive/%{version}/python-varlink-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-rpm-macros
BuildRequires:  python-setuptools

%if 0%{?build_py3}
BuildRequires:  python3-devel
BuildRequires:  python3-rpm-macros
%endif


%global _description \
An python module for Varlink with client and server support.

%description %_description

%package -n     python2-blkinfo-varlink
Summary:        %summary
%{?python_provide:%python_provide python2-blkinfo-varlink}


%if 0%{?build_py3}
%package -n python3-blkinfo-varlink
Summary:       %summary
%{?python_provide:%python_provide python3-blkinfo-varlink}
%endif

%description -n python2-blkinfo-varlink %_description

%if 0%{?build_py3}
%description -n python3-blkinfo-varlink %_description
%endif

%prep
%autosetup -n python-%{version}

%build
%if 0%{?build_py3}
%py3_build
%endif


%if 0%{?build_py3}
%check
CFLAGS="%{optflags}" %{__python3} %{py_setup} %{?py_setup_args} check
%endif

%install
%py2_install
%if 0%{?build_py3}
%py3_install
%endif

%files -n python2-blkinfo-varlink
%license LICENSE.txt
%doc README.md
%{python2_sitelib}/*

%if 0%{?build_py3}
%files -n python3-blkinfo-varlink
%license LICENSE.txt
%doc README.md
%{python3_sitelib}/*
%endif

%changelog
