package controllers

import (
	"context"
	"fmt"

	corev1 "k8s.io/api/core/v1"
	rbacv1 "k8s.io/api/rbac/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"
)

type TenantReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

func (r *TenantReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx)
	logger.Info("Reconciling Tenant", "name", req.NamespacedName)

	nsName := fmt.Sprintf("tenant-%s", req.Name)

	ns := &corev1.Namespace{
		ObjectMeta: metav1.ObjectMeta{
			Name: nsName,
			Labels: map[string]string{
				"genesis.ai/tenant":                          req.Name,
				"genesis.ai/managed-by":                      "genesis-operator",
				"pod-security.kubernetes.io/enforce":         "restricted",
				"pod-security.kubernetes.io/enforce-version": "latest",
			},
		},
	}

	if err := r.Create(ctx, ns); err != nil {
		if !errors.IsAlreadyExists(err) {
			logger.Error(err, "Failed to create namespace")
			return ctrl.Result{}, err
		}
	}

	rb := &rbacv1.RoleBinding{
		ObjectMeta: metav1.ObjectMeta{
			Name:      "tenant-admin",
			Namespace: nsName,
		},
		RoleRef: rbacv1.RoleRef{
			APIGroup: "rbac.authorization.k8s.io",
			Kind:     "ClusterRole",
			Name:     "admin",
		},
		Subjects: []rbacv1.Subject{
			{
				Kind: "Group",
				Name: fmt.Sprintf("tenant-%s-admins", req.Name),
			},
		},
	}

	if err := r.Create(ctx, rb); err != nil {
		if !errors.IsAlreadyExists(err) {
			logger.Error(err, "Failed to create RoleBinding")
			return ctrl.Result{}, err
		}
	}

	logger.Info("Tenant reconciled", "namespace", nsName)
	return ctrl.Result{}, nil
}

func Register(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		Named("tenant-controller").
		Complete(&TenantReconciler{
			Client: mgr.GetClient(),
			Scheme: mgr.GetScheme(),
		})
}
