%global commit 0ce5178770bea39b9c94ea9d83f4a11648fb82d0
%global date 20260706
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           ipu7-camera-hal
Summary:        IPU7 Hardware Abstraction Layer
Version:        0^%{date}git%{shortcommit}
Release:        9%{?dist}
License:        Apache-2.0
URL:            https://github.com/intel/ipu7-camera-hal
ExclusiveArch:  x86_64

Source0:        https://github.com/intel/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        72-ipu7-psys.rules
Source2:        50-ipu7-hide-raw-v4l2.conf
Source3:        libcamhal.conf

BuildRequires:  cmake
BuildRequires:  expat-devel
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  ipu7-camera-bins-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  kernel-headers
BuildRequires:  libdrm-devel
BuildRequires:  systemd-rpm-macros

# Components do not have matching snapshots, so just use something to satisfy dependencies:
Provides:       ipu7-kmod-common = 1
Provides:       vision-kmod-common = 1

Requires:       ipu7-camera-bins%{?_isa}
Requires:       ipu7-kmod
Requires:       libcamhal%{?_isa} = %{version}-%{release}
Requires:       wireplumber

%description
IPU7 Hardware Abstraction Layer plugins. They support MIPI cameras through the
IPU7 and IPU8 on Intel Lunar Lake, Panther Lake and Novalake platforms. The
plugins are loaded on demand by the libcamhal adaptor.

%package -n libcamhal
Summary:        Camera HAL adaptor library

%description -n libcamhal
libcamhal is the hardware abstraction layer adaptor. At runtime it detects the
Intel IPU present on the system and loads the matching IPU6, IPU7 or IPU8 HAL
plugin.

%package -n libcamhal-devel
Summary:        Header files for the camera HAL
Requires:       libcamhal%{?_isa} = %{version}-%{release}
Requires:       ipu7-camera-bins-devel
Provides:       ipu7-camera-hal-devel = %{version}-%{release}
Obsoletes:      ipu7-camera-hal-devel < %{version}-%{release}
Provides:       ipu6-camera-hal-devel = %{version}-%{release}
Obsoletes:      ipu6-camera-hal-devel < %{version}-%{release}

%description -n libcamhal-devel
This provides the necessary header files for camera HAL development.

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
install -p -m 0644 -D %{SOURCE3} %{buildroot}%{_tmpfilesdir}/libcamhal.conf

# Load the PSYS module at boot so /dev/ipu-psys0 is available (it does not
# auto-load); this covers both IPU7 and IPU8:
install -d %{buildroot}%{_modulesloaddir}
echo intel-ipu7-psys > %{buildroot}%{_modulesloaddir}/ipu7-psys.conf

# Filter out raw v4l2 devices (not usable) from the list of available cameras in Pipewire:
install -p -m 0644 -D %{SOURCE3} %{buildroot}%{_datadir}/wireplumber/wireplumber.conf.d/50-ipu7-hide-raw-v4l2.conf

%posttrans
if [ -x /usr/lib/systemd/systemd-update-helper ]; then
    /usr/lib/systemd/systemd-update-helper mark-restart-user-units wireplumber.service || :
    /usr/lib/systemd/systemd-update-helper user-restart || :
fi

%post -n libcamhal
%tmpfiles_create %{_tmpfilesdir}/libcamhal.conf

%files
%license LICENSE
%doc *.md
%{_datadir}/camera/
%{_libdir}/libcamhal/
%{_modulesloaddir}/ipu7-psys.conf
%{_udevrulesdir}/72-ipu7-psys.rules
%{_datadir}/wireplumber/wireplumber.conf.d/50-ipu7-hide-raw-v4l2.conf

%files -n libcamhal
%license LICENSE
%{_libdir}/libcamhal.so.0.0.0
%{_libdir}/libcamhal.so.0
%{_tmpfilesdir}/libcamhal.conf

%files -n libcamhal-devel
%{_includedir}/libcamhal/
%{_libdir}/libcamhal.so
%{_libdir}/pkgconfig/libcamhal.pc

%changelog
* Mon Jul 13 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-9
- Try with posttrans for restarting user's systemd units.

* Mon Jul 13 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-8
- Add wireplumber configuration to hide raw v4l2 devices.

* Thu Jul 09 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-7
- Load the intel-ipu7-psys module at boot through modules-load.d.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-6
- Provide vision-kmod-common to satisfy the akmod-vision dependency.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-5
- Provide ipu7-kmod-common to satisfy the akmod-ipu7 dependency.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-4
- Require the ipu7-kmod kernel modules.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-3
- Ship all Markdown documentation files.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-2
- Split the libcamhal adaptor and headers into libcamhal and libcamhal-devel
  subpackages, shared with ipu6-camera-hal.

* Wed Jul 08 2026 Simone Caronni <negativo17@gmail.com> - 0^20260706git0ce5178-1
- First build.
