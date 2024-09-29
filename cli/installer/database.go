package installer

import (
	"errors"
	"fmt"
	"github.com/syncloud/golib/linux"
	"go.uber.org/zap"
	"os"
	"path"
)

type Database struct {
	backupFile  string
	databaseDir string
	dumpCmd     string
	restoreCmd  string
	executor    *Executor
	logger      *zap.Logger
}

func NewDatabase(
	appDir string,
	dataDir string,
	executor *Executor,
	logger *zap.Logger,
) *Database {
	return &Database{
		backupFile:  path.Join(dataDir, "database.dump.gzip"),
		databaseDir: path.Join(dataDir, "mongodb"),
		dumpCmd:     path.Join(appDir, "mongodb/bin/mongodump.sh"),
		restoreCmd:  path.Join(appDir, "mongodb/bin/mongorestore.sh"),
		executor:    executor,
		logger:      logger,
	}
}

func (d *Database) DatabaseDir() string {
	return d.databaseDir
}

func (d *Database) Remove() error {
	if _, err := os.Stat(d.backupFile); errors.Is(err, os.ErrNotExist) {
		return fmt.Errorf("backup file does not exist: %s", d.backupFile)
	}
	_ = os.RemoveAll(d.databaseDir)
	return nil
}

func (d *Database) Init() error {
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
