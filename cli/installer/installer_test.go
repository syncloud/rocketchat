package installer

import (
	"github.com/stretchr/testify/assert"
	"path"
	"testing"
)

func TestArchSupported_armv82(t *testing.T) {
	pi5 := "Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp"
	assert.True(t, supported(pi5))
}

func TestArchSupported_armv80(t *testing.T) {
	pi4 := "Features\t: fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid"
	assert.False(t, supported(pi4))
}

func TestCheckArch_nonArmAlwaysOk(t *testing.T) {
	assert.NoError(t, NewCpuChecker("amd64", "/does/not/matter").Check())
}

func TestInitialized(t *testing.T) {
	tempDir := t.TempDir()

	installer := &Installer{
		installFile: path.Join(tempDir, "installer"),
	}
	assert.False(t, installer.IsInstalled())
	err := installer.MarkInstalled()
	assert.NoError(t, err)
	assert.True(t, installer.IsInstalled())
}
