package main

import (
	"os"

	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"

	"genesis/controllers"
	"genesis/webhook"
)

func main() {
	ctrl.SetLogger(zap.New(zap.UseDevMode(false)))

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		LeaderElection:   true,
		LeaderElectionID: "genesis-operator-lock",
	})
	if err != nil {
		ctrl.Log.Error(err, "unable to create manager")
		os.Exit(1)
	}

	if err := controllers.Register(mgr); err != nil {
		ctrl.Log.Error(err, "unable to register controllers")
		os.Exit(1)
	}

	webhook.Register(mgr)

	ctrl.Log.Info("Starting Genesis Operator", "version", "10.1.0")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		ctrl.Log.Error(err, "unable to start manager")
		os.Exit(1)
	}
}
