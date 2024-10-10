package installer

import (
	"errors"
	"fmt"
	"github.com/syncloud/golib/linux"
	"go.uber.org/zap"
	"os"
	"path"
	"time"
)

type Database struct {
	backupFile    string
	databaseDir   string
	dumpCmd       string
	initCmd       string
	restoreCmd    string
	mongoShellCmd string
	executor      *Executor
	logger        *zap.Logger
}

func NewDatabase(
	appDir string,
	dataDir string,
	executor *Executor,
	logger *zap.Logger,
) *Database {
	return &Database{
		backupFile:    path.Join(dataDir, "database.dump.gzip"),
		databaseDir:   path.Join(dataDir, "mongodb"),
		dumpCmd:       path.Join(appDir, "mongodb/bin/mongodump.sh"),
		restoreCmd:    path.Join(appDir, "mongodb/bin/mongorestore.sh"),
		mongoShellCmd: path.Join(appDir, "mongodb/bin/mongo.sh"),
		initCmd:       path.Join(appDir, "bin/mongo-init.sh"),
		executor:      executor,
		logger:        logger,
	}
}

func (d *Database) Remove() error {
	if _, err := os.Stat(d.backupFile); errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("backup file does not exist: %s", d.backupFile)
	}
	_ = os.RemoveAll(d.databaseDir)
	return nil
}

func (d *Database) Init() error {
	attempt := 0
	attempts := 10
	for attempt < attempts {
		attempt++
		err := d.executor.Run(d.initCmd)
		if err == nil {
			return nil
		}
		d.logger.Error("init failed", zap.Error(err), zap.Int("attempt", attempt))
		time.Sleep(10 * time.Second)
	}
	return fmt.Errorf("init failed after %d attempts", attempts)
}

func (d *Database) InitConfig() error {
	return linux.CreateMissingDirs(d.databaseDir)
}

func (d *Database) Restore() error {
	if _, err := os.Stat(d.backupFile); errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("backup file does not exist: %s", d.backupFile)
	}

	return d.executor.Run(d.restoreCmd,
		"--drop",
		fmt.Sprint("--archive=", d.backupFile),
		"--gzip")
}

func (d *Database) Backup() error {
	_ = os.RemoveAll(d.backupFile)
	return d.executor.Run(d.dumpCmd,
		fmt.Sprint("--archive=", d.backupFile),
		"--gzip")
}

func (d *Database) Update(key, value string) error {
	return d.executor.Run(d.mongoShellCmd,
		App,
		"--eval",
		fmt.Sprint("db.rocketchat_settings.update({'_id': '", key, "'}, {$set: {'value': '", value, "'}});"),
	)
}
