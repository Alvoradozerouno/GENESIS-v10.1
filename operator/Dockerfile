# GENESIS Kubernetes Operator - Multi-stage build
FROM golang:1.22-alpine AS builder

LABEL maintainer="GENESIS Team"
LABEL description="Kubernetes Operator for Multi-Tenant Management"

# Install build dependencies
RUN apk add --no-cache git make

# Set working directory
WORKDIR /workspace

# Copy go mod files
COPY go.mod go.mod
COPY go.sum go.sum

# Download dependencies
RUN go mod download

# Copy source code
COPY cmd/ cmd/
COPY api/ api/
COPY controllers/ controllers/
COPY webhook/ webhook/

# Build the operator
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o operator cmd/main.go

# Final stage - minimal runtime image
FROM gcr.io/distroless/static:nonroot

WORKDIR /
COPY --from=builder /workspace/operator .

USER 65532:65532

ENTRYPOINT ["/operator"]
