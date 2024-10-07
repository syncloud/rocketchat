package installer

import (
	"github.com/stretchr/testify/assert"
	"path"
	"testing"
)

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
