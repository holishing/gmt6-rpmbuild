%global gmthome %{_datadir}/gmt
%global gmtconf %{_sysconfdir}/gmt
%global gmtdoc %{_docdir}/gmt

%bcond_with octave
%if %with octave
%{!?octave_api: %global octave_api %(octave-config -p API_VERSION 2>/dev/null || echo 0)}
%global octave_mdir %(octave-config -p LOCALAPIFCNFILEDIR || echo)
%global octave_octdir %(octave-config -p LOCALAPIOCTFILEDIR || echo)
%endif

%global completion_dir %(pkg-config --variable=completionsdir bash-completion)
%if "%{completion_dir}" == ""
%global completion_dir "/etc/bash_completion.d"
%endif

Name:           GMT
Version:        5.1.2
Release:        1%{?dist}
Summary:        Generic Mapping Tools

License:        LGPLv3+
URL:            http://gmt.soest.hawaii.edu/
Source0:        ftp://ftp.soest.hawaii.edu/gmt/gmt-%{version}-src.tar.bz2
# Fix bash completion install location
Patch0:         GMT-bash-completion.patch

BuildRequires:  cmake
BuildRequires:  gdal-devel
BuildRequires:  libXt-devel libXaw-devel libXmu-devel libXext-devel
BuildRequires:  netcdf-devel
BuildRequires:  pcre-devel
BuildRequires:  dcw-gmt
BuildRequires:  gshhg-gmt-nc4
%if %with octave
BuildRequires:  octave-devel
%endif
# less is detected by configure, and substituted in GMT.in
BuildRequires:  less
Requires:       less
Requires:       %{name}-common = %{version}-%{release}
Requires:       dcw-gmt
Requires:       gshhg-gmt-nc4
Provides:       gmt = %{version}-%{release}
%if %without octave
Obsoletes:      GMT-octave <= 4.5.11
%endif

# Do not generate provides for plugins
%global __provides_exclude_from ^%{_libdir}/gmt/.*\\.so$

%description
GMT is an open source collection of ~60 tools for manipulating geographic and
Cartesian data sets (including filtering, trend fitting, gridding, projecting,
etc.) and producing Encapsulated PostScript File (EPS) illustrations ranging
from simple x-y plots via contour maps to artificially illuminated surfaces
and 3-D perspective views.  GMT supports ~30 map projections and transforma-
tions and comes with support data such as coastlines, rivers, and political
boundaries.

GMT is developed and maintained by Paul Wessel and Walter H. F.  Smith with
help from a global set of volunteers, and is supported by the National
Science Foundation.

NOTE: Specific executables that conflict with other Fedora packages have been
removed.  These functions can still be accessed via the GMT wrapper script
with: GMT <function> [args]


%package        common
Summary:        Common files for %{name}
Provides:       gmt-common = %{version}-%{release}
BuildArch:      noarch

%description    common
The %{name}-common package contains common files for GMT (Generic
Mapping Tools) package.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}
Provides:       gmt-devel = %{version}-%{release}
Obsoletes:      GMT-static <= 4.5.11

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        doc
Summary:        Documentation for %{name}
Requires:       %{name} = %{version}-%{release}
Provides:       gmt-doc = %{version}-%{release}
Provides:       %{name}-examples = %{version}-%{release}
Obsoletes:      %{name}-examples < %{version}-%{release}
BuildArch:      noarch

%description    doc
The %{name}-doc package provides the documentation for the GMT (Generic
Mapping Tools) package.


%if %with octave
%package        octave
Summary:        Octave libraries for %{name}
Requires:       %{name} = %{version}-%{release}
Requires:       octave(api) = %{octave_api}
Provides:       gmt-octave = %{version}-%{release}

%description    octave
The %{name}-octave package contains and Octave interface for developing
applications that use %{name}.
%endif


%prep
%setup -q -n gmt-%{version}
%patch0 -p1 -b .bash-completion


%build
mkdir build
pushd build
%{cmake} \
  -DGSHHG_ROOT=%{_prefix} \
  -DFLOCK=on \
  -DGMT_INSTALL_MODULE_LINKS=off \
  -DGMT_INSTALL_TRADITIONAL_FOLDERNAMES=off \
  -DGMT_MANDIR=%{_mandir} \
  -DLICENSE_RESTRICTED=LGPL \
%if %with octave
  -DGMT_OCTAVE=BOOL:ON \
%endif
  -DGMT_OPENMP=BOOL:ON \
  -DBASH_COMPLETION_DIR=%{completion_dir} \
  ..
make %{?_smp_mflags}


%install
make -C build DESTDIR=$RPM_BUILD_ROOT install
#Setup configuration files 
mkdir -p $RPM_BUILD_ROOT%{gmtconf}/{mgg,dbase,mgd77,conf}
pushd $RPM_BUILD_ROOT%{gmthome}/
# put conf files in %{gmtconf} and do links in %{gmthome}
for file in conf/*.conf mgg/gmtfile_paths dbase/grdraster.info \
    mgd77/mgd77_paths.txt; do
  mv $file $RPM_BUILD_ROOT%{gmtconf}/$file
  ln -s ../../../../../%{gmtconf}/$file $RPM_BUILD_ROOT%{gmthome}/$file
done
popd

# Don't ship .bat files
find $RPM_BUILD_ROOT -name \*.bat -delete


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%doc ChangeLog COPYING.LESSERv3 COPYINGv3 LICENSE.TXT README
%{_bindir}/*
%{_libdir}/*.so.5*
%{_libdir}/gmt/

%files common
%doc COPYING.LESSERv3 COPYINGv3 LICENSE.TXT
%dir %{gmtconf}
%dir %{gmtconf}/mgg
%dir %{gmtconf}/dbase
%dir %{gmtconf}/mgd77
%dir %{gmtconf}/conf
%config(noreplace) %{gmtconf}/conf/*
%config(noreplace) %{gmtconf}/mgg/gmtfile_paths
%config(noreplace) %{gmtconf}/dbase/grdraster.info 
%config(noreplace) %{gmtconf}/mgd77/mgd77_paths.txt
%{gmthome}/
%{completion_dir}/
%{_mandir}/man1/*.1*
%{_mandir}/man5/*.5*

%files devel
%{_includedir}/*
%{_libdir}/*.so
%{_mandir}/man3/*.3*

%files doc
%{gmtdoc}/

%if %with octave
%files octave
%{octave_mdir}/*.m
%{octave_octdir}/*.mex
%endif


%changelog
* Mon Jul 27 2015 Orion Poplawski <orion@cora.nwra.com> - 5.1.2-1
- Update to 5.1.2
- Add patch to fix bash completion install location
- Drop arch patch applied upstream

* Mon Jul 27 2015 Orion Poplawski <orion@cora.nwra.com> - 5.1.1-8
- Rebuild for gdal 2.0.0

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Oct 6 2014 Orion Poplawski - 5.1.1-6
- Fix arch patch for aarch64

* Sat Oct 4 2014 Dan Horák <dan[at]danny.cz> - 5.1.1-5
- Fix build on s390(x)

* Thu Sep 4 2014 Orion Poplawski - 5.1.1-4
- Add patch for multi-platform support

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Mar 2 2014 Orion Poplawski - 5.1.1-1
- Update to 5.1.1

* Thu Jan 2 2014 Orion Poplawski - 5.1.0-2
- Add patch to support arm

* Tue Dec 31 2013 Orion Poplawski - 5.1.0-1
- Update to 5.1.0
- Disable octave support - removed from upstream for now
- Drop xgridedit sub-package - removed from upstream

* Sat Dec 28 2013 Kevin Fenzi <kevin@scrye.com> - 4.5.11-2
- Rebuild to fix broken deps

* Sat Nov 9 2013 Orion Poplawski - 4.5.11-1
- Update to 4.5.11
- Drop includes patch fixed upstream
- Spec cleanup

* Tue Aug 27 2013 Orion Poplawski - 4.5.9-6
- Rebuild for gdal 1.10.0

* Fri Aug 02 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Mar 13 2013 Orion Poplawski <orion@cora.nwra.com> 4.5.9-4
- Drop triangulate binary to avoid conflicts (bug #913685)

* Tue Mar 12 2013 Orion Poplawski <orion@cora.nwra.com> 4.5.9-3
- Add another needed include (bug #920675)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Jan 22 2013 Orion Poplawski <orion@cora.nwra.com> 4.5.9-1
- Update to 4.5.9
- Add patch to add needed includes

* Tue Apr 3 2012 Orion Poplawski <orion@cora.nwra.com> 4.5.8-1
- Update to 4.5.8

* Mon Jan 16 2012 Orion Poplawski <orion@cora.nwra.com> 4.5.7-3
- Rebuild for octave 3.6.0

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Aug 12 2011 Orion Poplawski <orion@cora.nwra.com> 4.5.7-1
- Update to 4.5.7
- Drop triangulate patch applied upstream
- License is now (as of 4.5.6 actually) GPLv2 or later
- Re-enable octave support since we are GPLv3 compatible now

* Thu Mar 31 2011 Orion Poplawski <orion@cora.nwra.com> 4.5.6-2
- Rebuild for netcdf 4.1.2

* Thu Mar 10 2011 Orion Poplawski <orion@cora.nwra.com> 4.5.6-1
- Update to 4.5.6
- Add patch to avoid triangulate segfault on no or empty input (bug 681957).

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Nov 6 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.5-2
- Drop octave package due to licensing issues (bug 511844)

* Wed Nov 3 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.5-1
- Update to 4.5.5
- Drop bufoverflow patch fixed upstream

* Thu Jul 22 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.3-3
- Fix buffer overflow in psimage (bug #617332)

* Tue Jul 20 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.3-2
- Bump coastlines requirement to 2.1.0

* Mon Jul 19 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.3-1
- Update to 4.5.3

* Wed Jan 27 2010 Orion Poplawski <orion@cora.nwra.com> 4.5.2-1
- Update to 4.5.2

* Thu Nov 19 2009 Orion Poplawski <orion@cora.nwra.com> 4.5.1-3
- Re-enable check

* Thu Nov 19 2009 Orion Poplawski <orion@cora.nwra.com> 4.5.1-2
- Rebuild for netcdf 4.1.0
- Don't make GMT-common depend on GMT
- Remove BR GMT-coastlines, disable check for bootstrap

* Mon Oct 19 2009 Orion Poplawski <orion@cora.nwra.com> 4.5.1-1
- Update to 4.5.1
- Enable gdal support

* Fri Jul 31 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 4.5.0-4
- Rebuild against Octave 3.2.2

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Orion Poplawski <orion@cora.nwra.com> 4.5.0-1
- Update to 4.5.0

* Fri Apr 10 2009 Orion Poplawski <orion@cora.nwra.com> 4.4.0-2
- Add --enable-debug to avoid stripping of -g from CFLAGS

* Tue Feb 24 2009 Orion Poplawski <orion@cora.nwra.com> 4.4.0-1
- Update to 4.4.0
- Merge doc package into main package as noarch sub-packages
- Merge examples sub-package into doc

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue May 27 2008 Orion Poplawski <orion@cora.nwra.com> 4.3.1-2
- Fix lowercase provides (bug #448263)

* Wed May 21 2008 Orion Poplawski <orion@cora.nwra.com> 4.3.1-1
- Update to 4.3.1, drop upstreamed patches
- Remove other install fixes upstreamed

* Mon May 12 2008 Orion Poplawski <orion@cora.nwra.com> 4.3.0-2
- Add patch to link libraries properly
- Run ldconfig in %%post, dummy
- Don't ship .bat file
- Don't ship .in files
- Don't make .csh examples executable
- Drop execute bit on .m files

* Tue May 6 2008 Orion Poplawski <orion@cora.nwra.com> 4.3.0-1
- Update to 4.3.0, drop many upsreamed patches
- Add patch to install octave files in DESTDIR
- Add patch to fix segfaults due to uninitialized memory
- Add patch to fix a possible buffer overflow warning
- Remove duplicate html directory from examples package
- Create __package_docs directory for main package docs

* Tue Apr 29 2008 Orion Poplawski <orion@cora.nwra.com> 4.2.1-3
- Remove unfree source
- Split out xgridedit into sub-package
- Add BR and R on less
- Redirect octave-config stderr to /dev/null
- Move config files to /etc/GMT
- Use install -c -p to preserve timestamps
- Use cp -pr to copy share data
- Add sonames to shared libraries

* Mon Mar 24 2008 Orion Poplawski <orion@cora.nwra.com> 4.2.1-2
- Drop -doc sub-package, will have separate -docs package
- Add lower case name provides
- Build Octave files

* Mon Mar 17 2008 Orion Poplawski <orion@cora.nwra.com> 4.2.1-1
- Initial version
