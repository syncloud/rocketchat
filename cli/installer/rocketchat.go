package installer

import (
	"context"
	"fmt"
	"go.uber.org/zap"
	"net"
	"net/http"
	"time"
)

type RocketChat struct {
	appDir   string
	executor *Executor
	client   *http.Client
	logger   *zap.Logger
}

func NewRocketChat(appDir string, executor *Executor, logger *zap.Logger) *RocketChat {
	return &RocketChat{
		appDir:   appDir,
		executor: executor,
		client: &http.Client{
			Transport: &http.Transport{
				DialContext: func(_ context.Context, _, _ string) (net.Conn, error) {
					return net.Dial("unix", "/var/snap/rocketchat/common/web.socket")
				},
			},
		},
		logger: logger,
	}
}

func (c *RocketChat) DisableRegistration() error {
	err := c.waitFoRC()
	if err != nil {
		return err
	}
	c.logger.Info("disabling registration wizard")
	return c.executor.Run(
		fmt.Sprint(c.appDir, "/bin/mongo-disable-wizard.sh"),
	)
}

func (c *RocketChat) waitFoRC() error {
	attempt := 0
	attempts := 20
	for attempt < attempts {
		resp, err := c.client.Get("http://unix/status")
		if err == nil {
			if resp.StatusCode == 200 {
				c.logger.Info("RocketChat started")
				return nil
			}
			c.logger.Info("RocketChat API returned HTTP status, waiting", zap.Int("status", resp.StatusCode))
		}
		c.logger.Info("RocketChat API error, waiting", zap.Error(err))
		time.Sleep(10 * time.Second)
		attempts++
	}
	return fmt.Errorf("timeout waiting for RocketChat API to start")
}
