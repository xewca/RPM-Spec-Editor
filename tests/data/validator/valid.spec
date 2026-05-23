Name: test-package
Version: 1.0
Release: 1
Summary: Test package

License: MIT
Source0: test.tar.gz

BuildRequires: gcc
Requires: python3

%description
Test package description

%prep
%setup -q

%build
make

%install
make install

%files
/usr/bin/test