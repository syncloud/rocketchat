package installer

import (
	"context"
	"fmt"
	"go.uber.org/zap"
	"io"
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
	err = c.executor.Run(
		fmt.Sprint(c.appDir, "/mongodb/bin/mongo.sh"),
		fmt.Sprint(c.appDir, "/config/mongo.disable-wizard.js"),
	)
	if err != nil {
		return err
	}
	c.logger.Info("restarting rocketchat")
	err = c.executor.Run("snap", "restart", "rocketchat")
	if err != nil {
		return err
	}
	return c.waitFoRC()
}

func (c *RocketChat) waitFoRC() error {
	attempt := 0
	attempts := 20
	for attempt < attempts {
		resp, err := c.client.Get("http://unix/api/v1")
		if err == nil {
			if resp.StatusCode == 200 {
				defer resp.Body.Close()
				body, err := io.ReadAll(resp.Body)
				if err != nil {
					c.logger.Info("RocketChat started", zap.Error(err))
					return nil
				}
				c.logger.Info("RocketChat started", zap.String("resp", string(body)))
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
