package installer

import (
	"fmt"
	cp "github.com/otiai10/copy"
	"github.com/syncloud/golib/config"
	"github.com/syncloud/golib/linux"
	"github.com/syncloud/golib/platform"
	"go.uber.org/zap"
	"os"
	"path"
	"time"
)

const (
	App = "rocketchat"
)

type Variables struct {
	Domain           string
	DataDir          string
	AppDir           string
	CommonDir        string
	Url              string
	OIDCClientSecret string
	OIDCAuthUrl      string
	App              string
}

type Installer struct {
	oidcPasswordFile   string
	newVersionFile     string
	currentVersionFile string
	configDir          string
	platformClient     *platform.Client
	database           *Database
	installFile        string
	executor           *Executor
	appDir             string
	dataDir            string
	commonDir          string
	rocketChat         *RocketChat
	logger             *zap.Logger
}

func New(logger *zap.Logger) *Installer {
	appDir := fmt.Sprint("/snap/", App, "/current")
	dataDir := fmt.Sprint("/var/snap/", App, "/current")
	commonDir := fmt.Sprint("/var/snap/", App, "/common")
	configDir := path.Join(dataDir, "config")

	executor := NewExecutor(logger)
	return &Installer{
		oidcPasswordFile:   path.Join(dataDir, "oidc.password"),
		newVersionFile:     path.Join(appDir, "version"),
		currentVersionFile: path.Join(dataDir, "version"),
		configDir:          configDir,
		platformClient:     platform.New(),
		database:           NewDatabase(appDir, dataDir, executor, logger),
		installFile:        path.Join(commonDir, "installed"),
		executor:           executor,
		appDir:             appDir,
		dataDir:            dataDir,
		commonDir:          commonDir,
		rocketChat:         NewRocketChat(appDir, executor, logger),
		logger:             logger,
	}
}

func (i *Installer) Install() error {

	err := i.UpdateConfigs()
	if err != nil {
		return err
	}

	err = i.database.InitConfig()
	if err != nil {
		return err
	}

	err = i.FixPermissions()
	if err != nil {
		return err
	}

	return nil
}

func (i *Installer) Configure() error {
	if i.IsInstalled() {
		err := i.Upgrade()
		if err != nil {
			return err
		}
	} else {
		err := i.Initialize()
		if err != nil {
			return err
		}
	}

	err := i.FixPermissions()
	if err != nil {
		return err
	}

	err = i.UpdateVersion()
	if err != nil {
		return err
	}

	return i.DisableRegistration()
}

func (i *Installer) DisableRegistration() error {
	return i.rocketChat.DisableRegistration()
}

func (i *Installer) IsInstalled() bool {
	_, err := os.Stat(i.installFile)
	return err == nil
}

func (i *Installer) Initialize() error {
	err := i.database.Init()
	if err != nil {
		return err
	}

	err = i.StorageChange()
	if err != nil {
		return err
	}

	err = i.MarkInstalled()
	if err != nil {
		return err
	}

	return nil
}

func (i *Installer) MarkInstalled() error {
	return os.WriteFile(i.installFile, []byte("installed"), 0644)
}

func (i *Installer) Upgrade() error {
	err := i.database.Init()
	if err != nil {
		return err
	}

	err = i.database.Restore()
	if err != nil {
		return err
	}

	err = i.UpdateDbSettings()
	if err != nil {
		return err
	}

	err = i.StorageChange()
	if err != nil {
		return err
	}
	return nil
}

func (i *Installer) UpdateDbSettings() error {
	password, err := i.readOidcPassword()
	if err != nil {
		return err
	}

	err = i.database.Update("Accounts_OAuth_Custom-Syncloud-secret", password)
	if err != nil {
		return err
	}
	err = i.database.Update("Show_Setup_Wizard", "completed")
	if err != nil {
		return err
	}
	return nil
}

func (i *Installer) PreRefresh() error {
	return i.database.Backup()
}

func (i *Installer) PostRefresh() error {
	err := i.UpdateConfigs()
	if err != nil {
		return err
	}
	err = i.database.Remove()
	if err != nil {
		return err
	}
	err = i.database.InitConfig()
	if err != nil {
		return err
	}

	err = i.ClearVersion()
	if err != nil {
		return err
	}

	//TODO: fix missing install flag, remove after the release
	err = i.MarkInstalled()
	if err != nil {
		return err
	}

	err = i.FixPermissions()
	if err != nil {
		return err
	}
	return nil

}
func (i *Installer) AccessChange() error {
	err := i.UpdateConfigs()
	if err != nil {
		return err
	}

	err = i.UpdateDbSettings()
	if err != nil {
		return err
	}

	return nil
}

func (i *Installer) StorageChange() error {
	storageDir, err := i.platformClient.InitStorage(App, App)
	if err != nil {
		return err
	}
	err = linux.CreateMissingDirs(
		path.Join(storageDir, "tmp"),
		path.Join(i.dataDir, "plugins"),
		path.Join(i.dataDir, "client/plugins"),
	)
	if err != nil {
		return err
	}
	err = linux.Chown(storageDir, App)
	if err != nil {
		return err
	}

	return nil
}

func (i *Installer) ClearVersion() error {
	return os.RemoveAll(i.currentVersionFile)
}

func (i *Installer) UpdateVersion() error {
	return cp.Copy(i.newVersionFile, i.currentVersionFile)
}

func (i *Installer) UpdateConfigs() error {
	err := linux.CreateUser(App)
	if err != nil {
		return err
	}

	err = i.StorageChange()
	if err != nil {
		return err
	}

	domain, err := i.platformClient.GetAppDomainName(App)
	if err != nil {
		return err
	}

	url, err := i.platformClient.GetAppUrl(App)
	if err != nil {
		return err
	}

	authUrl, err := i.platformClient.GetAppUrl("auth")
	if err != nil {
		return err
	}

	password, err := i.platformClient.RegisterOIDCClient(App, "/_oauth/syncloud", false, "client_secret_post")
	if err != nil {
		return err
	}

	err = i.saveOidcPassword(password)
	if err != nil {
		return err
	}

	variables := Variables{
		Domain:           domain,
		DataDir:          i.dataDir,
		AppDir:           i.appDir,
		CommonDir:        i.commonDir,
		Url:              url,
		OIDCAuthUrl:      authUrl,
		OIDCClientSecret: password,
		App:              App,
	}

	err = config.Generate(
		path.Join(i.appDir, "config"),
		path.Join(i.dataDir, "config"),
		variables,
	)
	if err != nil {
		return err
	}

	return nil

}

func (i *Installer) FixPermissions() error {
	attempt := 0
	attempts := 10
	for attempt < attempts {
		attempt++
		err := i.FixPermissionsOnce()
		if err == nil {
			return nil
		}
		i.logger.Error("fix permissions failed", zap.Error(err), zap.Int("attempt", attempt))
		time.Sleep(1 * time.Second)
	}
	return fmt.Errorf("fix permissions failed after %d attempts", attempts)
}

func (i *Installer) FixPermissionsOnce() error {
	storageDir, err := i.platformClient.InitStorage(App, App)
	if err != nil {
		return err
	}

	err = linux.Chown(i.dataDir, App)
	if err != nil {
		return err
	}
	err = linux.Chown(i.commonDir, App)
	if err != nil {
		return err
	}

	err = linux.Chown(storageDir, App)
	if err != nil {
		return err
	}

	return nil
}

func (i *Installer) BackupPreStop() error {
	return i.PreRefresh()
}

func (i *Installer) RestorePreStart() error {
	return i.PostRefresh()
}

func (i *Installer) RestorePostStart() error {
	return i.Configure()
}

func (i *Installer) saveOidcPassword(value string) error {
	return os.WriteFile(i.oidcPasswordFile, []byte(value), 0644)
}

func (i *Installer) readOidcPassword() (string, error) {
	content, err := os.ReadFile(i.oidcPasswordFile)
	if err != nil {
		return "", err
	}
	return string(content), nil
}
