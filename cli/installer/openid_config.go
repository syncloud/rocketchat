package installer

import "encoding/json"

type Config struct {
	Connect Connect `json:"openid_connect"`
}

type Connect struct {
	Apps  []ConnectApp `json:"APPS"`
	Scope []string     `json:"SCOPE"`
}

type ConnectApp struct {
	ProviderID string   `json:"provider_id"`
	Name       string   `json:"name"`
	ClientID   string   `json:"client_id"`
	Secret     string   `json:"secret"`
	Settings   Settings `json:"settings"`
}

type Settings struct {
	ServerURL string `json:"server_url"`
}

func OpenIDConfig(url, clientID, secret string) (string, error) {
	config := Config{
		Connect: Connect{
			Apps: []ConnectApp{{
				ProviderID: "authelia",
				Name:       "Syncloud",
				ClientID:   clientID,
				Secret:     secret,
				Settings: Settings{
					ServerURL: url,
				},
			}},
			Scope: []string{
				"openid",
				"profile",
				"email",
				"groups",
			},
		},
	}
	b, err := json.Marshal(config)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
