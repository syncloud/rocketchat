package installer

import (
	"fmt"
	"os"
	"strings"
)

type CpuChecker struct {
	goarch      string
	cpuinfoPath string
}

func NewCpuChecker(goarch, cpuinfoPath string) *CpuChecker {
	return &CpuChecker{
		goarch:      goarch,
		cpuinfoPath: cpuinfoPath,
	}
}

func (c *CpuChecker) Check() error {
	if c.goarch != "arm64" {
		return nil
	}
	data, err := os.ReadFile(c.cpuinfoPath)
	if err != nil {
		return nil
	}
	if supported(string(data)) {
		return nil
	}
	return fmt.Errorf("unsupported CPU: rocketchat requires an ARMv8.2-A CPU " +
		"(Raspberry Pi 5, Odroid C4/HC4/M1, AWS Graviton2+, ...). This device looks like " +
		"ARMv8.0-A (e.g. Raspberry Pi 4 / Cortex-A72), which MongoDB 8 does not support. " +
		"Aborting to keep any existing installation working")
}

func supported(cpuinfo string) bool {
	for _, feature := range []string{"asimddp", "atomics", "asimdhp"} {
		if strings.Contains(cpuinfo, feature) {
			return true
		}
	}
	return false
}
