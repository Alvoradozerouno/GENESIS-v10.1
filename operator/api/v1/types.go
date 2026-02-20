package v1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

type TenantSpec struct {
	DisplayName          string   `json:"displayName"`
	Quota                string   `json:"quota,omitempty"`
	OIDCGroup            string   `json:"oidcGroup,omitempty"`
	Isolation            string   `json:"isolation"`
	ESGEnabled           bool     `json:"esgEnabled,omitempty"`
	ComplianceFrameworks []string `json:"complianceFrameworks,omitempty"`
}

type TenantStatus struct {
	Phase           string  `json:"phase,omitempty"`
	Namespace       string  `json:"namespace,omitempty"`
	FalcoEnabled    bool    `json:"falcoEnabled,omitempty"`
	SpireRegistered bool    `json:"spireRegistered,omitempty"`
	BackupScheduled bool    `json:"backupScheduled,omitempty"`
	ESGScore        float64 `json:"esgScore,omitempty"`
	LastAudit       string  `json:"lastAudit,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
type Tenant struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`
	Spec              TenantSpec   `json:"spec,omitempty"`
	Status            TenantStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true
type TenantList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []Tenant `json:"items"`
}
