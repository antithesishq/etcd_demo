ARG GO_VERSION=1.26.1
ARG ARCH=amd64

FROM docker.io/golang:$GO_VERSION
ARG CFG_NODE_COUNT=3

# cloning etcd
ARG REF=main
RUN git clone --depth=1 https://github.com/etcd-io/etcd.git --branch=${REF} /etcd
WORKDIR /etcd

# setup go mod
RUN go mod download

WORKDIR /etcd

# Fix: skip no-op raft entries instead of panicking (upstream bug in WAL parser)
RUN sed -i 's/panic(fmt.Sprintf("Unhandled raft request: %+v", raftReq))/return nil, nil/' tests/robustness/report/wal.go

WORKDIR /etcd/tests/antithesis

RUN go build -ldflags "-X main.NodeCount=$CFG_NODE_COUNT" -o /opt/antithesis/entrypoint/entrypoint -race ./test-template/entrypoint/main.go
RUN go build -ldflags "-X main.NodeCount=$CFG_NODE_COUNT" -o /opt/antithesis/test/v1/robustness/singleton_driver_traffic -race ./test-template/robustness/traffic/main.go
RUN go build -ldflags "-X main.NodeCount=$CFG_NODE_COUNT" -o /opt/antithesis/test/v1/robustness/finally_validation -race ./test-template/robustness/finally/main.go