package main

import (
	"fmt"
	"github.com/spf13/cobra"
	"github.com/syncloud/golib/log"
	"hooks/installer"
	"os"
)

func main() {
	logger := log.Logger()
	var rootCmd = &cobra.Command{
		SilenceUsage: true,
		RunE: func(cmd *cobra.Command, args []string) error {
			return installer.New(logger).PreRefresh()
		},
	}

	err := rootCmd.Execute()
	if err != nil {
		fmt.Print(err)
		os.Exit(1)
	}
}
