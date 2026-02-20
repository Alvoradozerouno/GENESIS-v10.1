package webhook

import (
	"context"
	"encoding/json"
	"net/http"

	admissionv1 "k8s.io/api/admission/v1"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/webhook"
	"sigs.k8s.io/controller-runtime/pkg/webhook/admission"
)

type TenantValidator struct {
	decoder *admission.Decoder
}

func (v *TenantValidator) Handle(ctx context.Context, req admission.Request) admission.Response {
	if req.Operation == admissionv1.Delete {
		return admission.Allowed("delete permitted")
	}

	if len(req.Object.Raw) == 0 {
		return admission.Denied("empty object")
	}

	var obj map[string]interface{}
	if err := json.Unmarshal(req.Object.Raw, &obj); err != nil {
		return admission.Denied("invalid JSON: " + err.Error())
	}

	spec, ok := obj["spec"].(map[string]interface{})
	if !ok {
		return admission.Denied("spec is required")
	}

	displayName, ok := spec["displayName"].(string)
	if !ok || displayName == "" {
		return admission.Denied("spec.displayName is required and must be non-empty")
	}

	isolation, ok := spec["isolation"].(string)
	if !ok {
		return admission.Denied("spec.isolation is required")
	}

	validIsolation := map[string]bool{"namespace": true, "cluster": true, "network": true}
	if !validIsolation[isolation] {
		return admission.Denied("spec.isolation must be one of: namespace, cluster, network")
	}

	return admission.Allowed("tenant validated")
}

type TenantMutator struct {
	decoder *admission.Decoder
}

func (m *TenantMutator) Handle(ctx context.Context, req admission.Request) admission.Response {
	var obj map[string]interface{}
	if err := json.Unmarshal(req.Object.Raw, &obj); err != nil {
		return admission.Errored(http.StatusBadRequest, err)
	}

	spec, ok := obj["spec"].(map[string]interface{})
	if !ok {
		spec = make(map[string]interface{})
		obj["spec"] = spec
	}

	if _, exists := spec["quota"]; !exists {
		spec["quota"] = "medium"
	}

	if _, exists := spec["isolation"]; !exists {
		spec["isolation"] = "namespace"
	}

	if _, exists := spec["esgEnabled"]; !exists {
		spec["esgEnabled"] = false
	}

	patched, err := json.Marshal(obj)
	if err != nil {
		return admission.Errored(http.StatusInternalServerError, err)
	}

	return admission.PatchResponseFromRaw(req.Object.Raw, patched)
}

func Register(mgr ctrl.Manager) {
	hookServer := mgr.GetWebhookServer()

	hookServer.Register("/validate-tenant", &webhook.Admission{
		Handler: &TenantValidator{},
	})

	hookServer.Register("/mutate-tenant", &webhook.Admission{
		Handler: &TenantMutator{},
	})
}
