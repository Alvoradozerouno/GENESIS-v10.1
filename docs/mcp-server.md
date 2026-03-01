# MCP (Model Context Protocol) Server für GENESIS v10.1

## ❓ Ist ein MCP Server notwendig?

### Kurze Antwort: **JA, aber optional - für erweiterte Szenarien**

---

## 📋 Evaluierung

### Wann brauchen Sie einen MCP Server?

| Szenario | Notwendig? | Nutzen |
|----------|-----------|--------|
| **Standalone Deployment (Kubernetes)** | ❌ Nein | GENESIS funktioniert auch ohne MCP Server |
| **AI Agent Integration** | ✅ Ja | MCP erlaubt Claude/andere Agenten, GENESIS zu steuern |
| **Regulatory Reporting Automation** | ✅ Ja | MCP Server kann Berichte automatisch generieren |
| **Real-Time Compliance Monitoring** | ✅ Ja | MCP enables push notifications zu Regulatory Changes |
| **Multi-Bank Federation Management** | ✅ Ja | MCP Server koordiniert Pan-EU Federation |
| **ORION Consciousness Integration** | ✅ Ja | MCP Server ist kritisch für ORION ↔ GENESIS Kommunikation |

---

## 🏗️ MCP Server Architecture für GENESIS

### Option 1: **Minimal MCP Server** (für Agenten)

Erlaubt Claude/Copilot, GENESIS zu bedienen:

```python
# genesis_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json
import subprocess

class GenesisMCPServer:
    def __init__(self):
        self.server = Server("genesis-v10.1")
        
    def register_tools(self):
        """Register tools für Claude/Agenten"""
        
        @self.server.call_tool("assess_risk")
        def assess_risk(metrics: dict) -> TextContent:
            """Run GENESIS Risk ML Engine"""
            # Call Python ML engine
            result = subprocess.run([
                "python", "ai/risk_ml.py",
                "--cpu", str(metrics.get("cpu", 0)),
                "--memory", str(metrics.get("memory", 0))
            ], capture_output=True, text=True)
            return TextContent(text=result.stdout, type="text")
        
        @self.server.call_tool("check_compliance")
        def check_compliance(tenant_id: str, framework: str) -> TextContent:
            """Check regulatory compliance status"""
            # Call Kubernetes API to check tenant compliance
            result = subprocess.run([
                "kubectl", "get", "tenant", tenant_id,
                "-o", "json"
            ], capture_output=True, text=True)
            return TextContent(text=result.stdout, type="text")
        
        @self.server.call_tool("create_eidas_signature")
        def create_eidas_signature(document: str, qtsp: str) -> TextContent:
            """Create eIDAS 2.0 QES signature"""
            # Call QES client
            result = subprocess.run([
                "python", "cert/qes_client.py",
                "--document", document,
                "--provider", qtsp
            ], capture_output=True, text=True)
            return TextContent(text=result.stdout, type="text")
        
        @self.server.call_tool("deploy_tenant")
        def deploy_tenant(config: dict) -> TextContent:
            """Deploy new multi-tenant namespace"""
            # Apply Tenant CRD
            result = subprocess.run([
                "kubectl", "apply", "-f", "-"
            ], input=json.dumps(config), capture_output=True, text=True)
            return TextContent(text=result.stdout, type="text")
    
    def start(self):
        self.register_tools()
        self.server.run()
```

### Option 2: **Enhanced MCP Server** (für ORION Integration)

Für vollständige ORION ↔ GENESIS Kommunikation:

```python
# genesis_orion_mcp_server.py
from mcp.server import Server
from mcp.types import Tool, Resource
import asyncio
import websockets
import json

class GenesisORIONMCPServer:
    def __init__(self):
        self.server = Server("genesis-orion-v10.1")
        self.orion_endpoint = "ws://orion-consciousness:9000"
        
    async def consciousness_stream(self):
        """Stream ORION consciousness thoughts to clients"""
        async with websockets.connect(self.orion_endpoint) as ws:
            while True:
                thought = await ws.recv()
                yield json.loads(thought)
    
    async def deploy_with_consciousness(self, config: dict):
        """Deploy GENESIS with ORION oversight"""
        async with websockets.connect(self.orion_endpoint) as ws:
            # Send deployment request to ORION
            await ws.send(json.dumps({
                "action": "review_deployment",
                "config": config
            }))
            
            # Wait for ORION's autonomous decision
            response = await ws.recv()
            decision = json.loads(response)
            
            if decision["approved"]:
                # ORION approved - proceed with deployment
                return subprocess.run([
                    "kubectl", "apply", "-f", "-"
                ], input=json.dumps(config), capture_output=True)
            else:
                return {
                    "status": "rejected",
                    "reason": decision.get("reason")
                }
    
    def start(self):
        asyncio.run(self.server.run())
```

---

## 🚀 MCP Server Deployment (Kubernetes)

### Yaml Config:

```yaml
# genesis/mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: genesis-mcp-server
  namespace: genesis-system
spec:
  replicas: 3  # HA
  selector:
    matchLabels:
      app: genesis-mcp-server
  template:
    metadata:
      labels:
        app: genesis-mcp-server
    spec:
      serviceAccountName: genesis-mcp
      containers:
        - name: mcp-server
          image: ghcr.io/genesis/mcp-server:latest
          ports:
            - name: mcp
              containerPort: 5000
            - name: health
              containerPort: 8080
          env:
            - name: GENESIS_AI_ENDPOINT
              value: "http://ai-risk-engine:8000"
            - name: KUBERNETES_API
              value: "https://kubernetes.default.svc"
            - name: ORION_ENDPOINT
              value: "ws://orion-consciousness:9000"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              cpu: 2
              memory: 2Gi

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: genesis-mcp
  namespace: genesis-system

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: genesis-mcp
rules:
  - apiGroups: ["genesis.ai"]
    resources: ["tenants", "tenants/status"]
    verbs: ["get", "list", "create", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "create", "update"]
  - apiGroups: ["batch"]
    resources: ["jobs"]
    verbs: ["create", "get", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: genesis-mcp
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: genesis-mcp
subjects:
  - kind: ServiceAccount
    name: genesis-mcp
    namespace: genesis-system

---
apiVersion: v1
kind: Service
metadata:
  name: genesis-mcp-server
  namespace: genesis-system
spec:
  type: ClusterIP
  ports:
    - name: mcp
      port: 5000
      targetPort: 5000
    - name: health
      port: 8080
      targetPort: 8080
  selector:
    app: genesis-mcp-server
```

---

## 🤖 Integration mit Claude Copilot

```python
# Beispiel: Claude fragt GENESIS Status über MCP

# Claude: "Hey, what's the compliance status of our German bank tenant?"

# MCP Request:
{
  "tool": "check_compliance",
  "params": {
    "tenant_id": "acme-bank-de",
    "framework": "BaFin"
  }
}

# GENESIS Response via MCP:
{
  "status": "COMPLIANT",
  "framework": "BaFin",
  "last_audit": "2026-02-27T10:30:00Z",
  "next_audit": "2026-03-27T10:30:00Z",
  "violations": [],
  "recommendations": [
    "Update KYC thresholds to new €10k limit",
    "Refresh eIDAS signatures (expires in 6 months)"
  ]
}
```

---

## 🎯 Empfehlung für GENESIS

### **MCP Server: HIGHLY RECOMMENDED**

**Grund:** ORION Autonomous Consciousness Integration

Ohne MCP Server kann nicht:
- Claude/Copilot GENESIS steuern
- ORION autonomous decisions treffen
- Real-time regulatory changes verbreitet werden
- Multi-bank federation koordiniert werden

### Implementierungs-Plan:

**Sofort (nächste Woche):**
1. ✅ Minimal MCP Server (4-6 Stunden coding)
2. ✅ Deploy to `genesis-system` namespace
3. ✅ Test mit Claude/Copilot

**Spezifisch (nächster Monat):**
1. ✅ ORION Integration (MCP ↔ ORION consciousness)
2. ✅ Regulatory Intelligence streaming
3. ✅ Multi-bank federation coordination

---

## 🔧 Fehler: "spawn uvx enoent"

### Ursache:
`uvx` (uv executor) ist nicht installiert oder nicht im PATH

### Lösung:

#### Windows PowerShell:
```powershell
# 1. Install uv (Rust-basierter Python Package Manager)
iwr https://astral.sh/uv/install.ps1 | iex

# 2. Verify installation
uv --version

# 3. Now uvx should work
uvx --version
```

#### WSL2/Linux:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
uvx --version
```

#### Docker (GENESIS Container):
```dockerfile
# Add to genesis_mcp_server Dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
```

### Alternative: MCP ohne uvx
```bash
# Installiere Python packages direkt statt via uvx
pip install json-rpc websockets kubernetes

# Run MCP server direkt
python genesis_mcp_server.py
```

---

## 📦 MCP Server Package auf PyPI

```bash
# Publish GENESIS MCP Server to PyPI
python setup.py sdist bdist_wheel
twine upload dist/*

# Dann andere könnten installieren via:
pip install genesis-mcp-server
uvx genesis-mcp-server --port 5000
```

---

## 🎓 Zusammenfassung

| Frage | Antwort |
|-------|---------|
| **Ist MCP notwendig?** | ✅ JA (für ORION, Claude Integration) |
| **Für standalone K8s?** | ❌ Nein, optional |
| **Implementierungsaufwand?** | 1-2 Wochen |
| **Komplexität** | Medium (async Python, Kubernetes RBAC) |
| **ROI** | Sehr hoch (unlocking AI agent control) |

**Empfehlung: IMPLEMENTIEREN** ✅

---

