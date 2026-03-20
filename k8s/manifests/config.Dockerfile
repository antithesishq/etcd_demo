FROM scratch

COPY ./client.yaml /manifests/client.yaml
COPY ./etcd.yaml /manifests/etcd.yaml