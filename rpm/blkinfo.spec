#### NOTE: if building locally you may need to do the following:
####
#### yum install rpmdevtools -y
#### spectool -g -R blkinfo.spec
####
#### At this point you can use rpmbuild -ba blkinfo.spec
#### (this is because our Source0 is a remote source)
%global pypi_name blkinfo

Name:           python-%{pypi_name}
Version:        0.0.7
Release:        1%{?dist}
Summary:        blkinfo is a python package to list information about all available or the specified block devices

License:        GPLv3
URL:            https://github.com/grinrag/blkinfo
Source0:        https://files.pythonhosted.org/packages/source/b/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)

%description
 Block Devices Information Aboutblkinfo is a python package to list information
about all available or the specified block devices.It bases on lsblk command
line tool, provided by util-linux, in addition, it collects information about
block devices, using /sys/block, /sys/devices, /proc directories.The main goal
is to provide Python's binding to lsblk. Old versions of lsblk, provided by...

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Provides: python3dist(%{pypi_name})

%description -n python3-%{pypi_name}
 Block Devices Information Aboutblkinfo is a python package to list information
about all available or the specified block devices.It bases on lsblk command
line tool, provided by util-linux, in addition, it collects information about
block devices, using /sys/block, /sys/devices, /proc directories.The main goal
is to provide Python's binding to lsblk. Old versions of lsblk, provided by...


%prep
%autosetup -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py3_build

%install
%py3_install

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info
