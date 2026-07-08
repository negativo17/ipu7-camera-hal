%global commit 0ce5178770bea39b9c94ea9d83f4a11648fb82d0
%global date 20260706
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu7-camera-hal
Summary:        IPU7 Hardware Abstraction Layer
Version:        0^%{date}git%{shortcommit}
Release:        1%{?dist}
License:        Apache-2.0
URL:            https://github.com/intel/ipu7-camera-hal
ExclusiveArch:  x86_64

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        72-ipu7-psys.rules
Source2:        ipu7-camera-hal.conf

BuildRequires:  cmake
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  ipu7-camera-bins-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  kernel-headers
BuildRequires:  libdrm-devel
BuildRequires:  systemd-rpm-macros

Requires:       ipu7-camera-bins%{?_isa}

%description
IPU7 Hardware Abstraction Layer. It supports MIPI cameras through the IPU7 on
Intel Lunar Lake and Panther Lake platforms.

%package devel
Summary:        IPU7 header files for HAL
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       ipu7-camera-bins-devel

%description devel
This provides the necessary header files for IPU7 HAL development.

%prep
%autosetup -p1 -n %{name}-%{commit}

# Fedora ships the jsoncpp headers under json/ instead of jsoncpp/json/
sed -i 's|<jsoncpp/json/json.h>|<json/json.h>|' src/platformdata/JsonParserBase.h

%build
export CFLAGS="%{optflags} -Wno-error=unused-but-set-variable"
export CXXFLAGS="%{optflags} -Wno-error=alloc-size-larger-than=9223372036854775807 -Wno-error=unused-but-set-variable"
%cmake \
  -DBUILD_CAMHAL_ADAPTOR=ON \
  -DBUILD_CAMHAL_PLUGIN=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_SYSCONFDIR=%{_datadir} \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -DIPU_VERSIONS="ipu7x;ipu75xa;ipu8" \
  -DUSE_STATIC_GRAPH=ON \
  -DUSE_STATIC_GRAPH_AUTOGEN=ON

%cmake_build

%install
%cmake_install

install -p -m 0644 -D %{SOURCE1} %{buildroot}%{_udevrulesdir}/72-ipu7-psys.rules
install -p -m 0644 -D %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf

%post
%tmpfiles_create %{_tmpfilesdir}/%{name}.conf

%files
%license LICENSE
%{_datadir}/camera/
%{_libdir}/libcamhal.so.0.0.0
%{_libdir}/libcamhal.so.0
%{_libdir}/libcamhal/
%{_tmpfilesdir}/%{name}.conf
%{_udevrulesdir}/72-ipu7-psys.rules

%files devel
%{_includedir}/libcamhal/
%{_libdir}/libcamhal.so
%{_libdir}/pkgconfig/libcamhal.pc

%changelog
* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-1
- First build.
