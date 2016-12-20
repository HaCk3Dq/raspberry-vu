pkgname=spectrumyzer
pkgver=1
pkgrel=1
pkgdesc="Spectrum analyzer rendered on a desktop"
arch=('x86_64' 'i686')
url="https://github.com/HaCk3Dq/spectrumyzer"
license=('GPL')
depends=('python2' 'cairo' 'python2-cairo' 'python2-gobject' 'fftw' 'libpulse')
makedepends=('git')
optdepends=()
provides=("$pkgname")
conflicts=()

source=("git+https://github.com/HaCk3Dq/spectrumyzer")
md5sums=('SKIP')

_gitname=spectrumyzer

build() {
  cd "$srcdir/$_gitname"
  make
}

package() {
  cd "$srcdir/$_gitname"
  mkdir -p "${pkgdir}/usr/bin"
  mkdir -p "${pkgdir}/usr/lib/python2.7"
  cp spectrumyzer.py "${pkgdir}/usr/bin/spectrumyzer"
  cp impulse.so "${pkgdir}/usr/lib/python2.7/impulse.so"
}
