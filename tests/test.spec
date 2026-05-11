Name:         test-pkg
Summary:      Test package.

License:      MIT

Release:     1

Version:     1.1.1

URL:         https://example.com/

BuildRequires: python3-devel
BuildRequires: PyQt5

%description
Test spec file 
description

%check

%files
%{_bindir}/%{name}-%{version}


%changelog
* Tue 3 Mar 2026 Vsevolod Mikheev
- Init new test package