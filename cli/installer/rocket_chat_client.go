package installer

import (
	"context"
	"go.uber.org/zap"
	"io"
	"net"
	"net/http"
	"time"
)

type RocketChatClient struct {
	client *http.Client
	logger *zap.Logger
}

func NewRocketChatClient(logger *zap.Logger) *RocketChatClient {
	return &RocketChatClient{
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

func (c *RocketChatClient) WaitForStartup() {
	attempt := 0
	attempts := 100
	for attempt < attempts {
		resp, err := c.client.Get("http://unix/api/v1")
		if err == nil {
			if resp.StatusCode == 200 {
				defer resp.Body.Close()
				body, err := io.ReadAll(resp.Body)
				if err != nil {
					c.logger.Info("RocketChat started", zap.Error(err))
					return
				}
				c.logger.Info("RocketChat started", zap.String("resp", string(body)))
				return
			}
			c.logger.Info("RocketChat API returned HTTP status, waiting", zap.Int("status", resp.StatusCode))
		}
		c.logger.Info("RocketChat API error, waiting", zap.Error(err))
		time.Sleep(10 * time.Second)
		attempts++
	}

}
