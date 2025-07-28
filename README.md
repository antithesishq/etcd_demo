# Antithesis etcd demo

This repository is forked from ([https://github.com/etcd-io/etcd/tree/main/tests/antithesis](https://github.com/etcd-io/etcd/tree/main/tests/antithesis)). It is meant to run previous releases of etcd version to find previously known issues (Brown M&Ms).


## Building and running the tests

* There is a github action job that builds all of the container images Monday morning to ensure container image retention. If you need to build custom versions of etcd please look into the `Makefile`
* Tests can be run via [github action](https://github.com/antithesishq/etcd_demo/actions/workflows/run_antithesis_test.yml) 
* (todo) Run multiverse debugging session
* (todo) Run bug report

## Known issue and new bugs found

The robustness tests mostly focused on guarantees of the watch API. A event-based API component of etcd. https://etcd.io/docs/v3.6/learning/api/#watch-api

We were able to break the following guarantees:

* **Bookmarkable** - Progress notification events guarantee that all events up to a revision have been already delivered
* **Reliable** - A sequence of events will never drop any subsequence of events; if there are events ordered in time as a < b < c, then if the watch receives events a and c, it is guaranteed to receive b
* **Resumable** - A broken watch can be resumed by establishing a new watch starting after the last revision received in a watch event before the break, so long as the revision is in the history window
* **Unique** - an event will never appear on a watch twice
* **Ordered** - events are ordered by revision; an event will never appear on a watch if it precedes an event in time that has already been posted


Below are the issues Antithesis helped Linux Foundation (etcd) found:

| **Guarantee Violated**   | **Original Issue**                                           | Found version(s) | Fixed Version | Antithesis report                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|-----------------|--------------------------------------------------------------|------------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Bookmarkable    | [github issue](https://github.com/etcd-io/etcd/issues/15220) | v3.5.0           | v3.5.8        | [Triage report](https://public.antithesis.com/report/LcKmbhrCiBLCksKxwq7CpsK3woLCkMKWenLDu14/BsUY10JF0LHQETvugI5DimDIzO47z16c0Lm2HXqK8vg.html)                                                                                                                                                                                                                                                                                                                              |
| Reliable        | [github issue](https://github.com/etcd-io/etcd/issues/18089) | v3.5.0, v3.5.8   | v3.5.16       | [Triage report](https://public.antithesis.com/report/w7dof2fCrSpLPHHDk8KICsOeAhDDjFnCjA/AmNyFPuJjv2dM7LJ8CSMpvIBX6JTzavqA4e9B5ZGEz0.html)                                                                                                                                                                                                                                                                                                                                   |
| Resumable (new issue) | [github issue](https://github.com/etcd-io/etcd/issues/20221) | v3.6.1           | v3.6.2        | [Triage report](https://linuxfoundation.antithesis.com/report/UZjUP_KGxboJepL7k1q_8pa4/ZqL0Vt9a7YESiiBmGecPMkBP8YgM1IwlTZJ4dcYjmZ8.html?auth=v2.public.eyJuYmYiOiIyMDI1LTA2LTI1VDAzOjE4OjIzLjM4MDU2MDQwMFoiLCJzY29wZSI6eyJSZXBvcnRTY29wZVYxIjp7ImFzc2V0IjoiWnFMMFZ0OWE3WUVTaWlCbUdlY1BNa0JQOFlnTTFJd2xUWko0ZGNZam1aOC5odG1sIiwicmVwb3J0X2lkIjoiVVpqVVBfS0d4Ym9KZXBMN2sxcV84cGE0In19feIAsYO4-UIigcL4eMu7QUqA6XFbCU3Hnw7BeyZW06o9x11mFqleHbSbRWdIcLdTH2Xzx42DXNB7dBqYq25Ujg4) |
| Unique          | [github issue](https://github.com/etcd-io/etcd/issues/18667) | v3.5.0           | v3.5.15?      | [Triage report](https://public.antithesis.com/report/LcKmbhrCiBLCksKxwq7CpsK3woLCkMKWenLDu14/BsUY10JF0LHQETvugI5DimDIzO47z16c0Lm2HXqK8vg.html)                                                                                                                                                                                                                                                                                                                              |
| Ordered         | N/A                                                          | v3.5.0           | ??            | [Triage report](https://public.antithesis.com/report/LcKmbhrCiBLCksKxwq7CpsK3woLCkMKWenLDu14/BsUY10JF0LHQETvugI5DimDIzO47z16c0Lm2HXqK8vg.html)                                                                                                                                                                                                                                                                                                                              |

---
---

## Original Read me


This directory enables integration of Antithesis with etcd. There are 4 containers running in this system: 3 that make up an etcd cluster (etcd0, etcd1, etcd2) and one that "[makes the system go](https://antithesis.com/docs/getting_started/basic_test_hookup/)" (client).

## Quickstart

### 1. Build and Tag the Docker Image

Run this command from the `antithesis/test-template` directory:

```bash
make antithesis-build-client-docker-image
make antithesis-build-etcd-image
```

Both commands build etcd-server and etcd-client from the current branch. To build a different version of etcd you can use:

```bash
make antithesis-build-etcd-image REF=${GIT_REF} 
```

### 2. (Optional) Check the Image Locally

You can verify your new image is built:

```bash
docker images | grep etcd-client
```

It should show something like:

```
etcd-client        latest    <IMAGE_ID>    <DATE>
```

### 3. Use in Docker Compose

Run the following command from the root directory for Antithesis tests (`tests/antithesis`):

```bash
make antithesis-docker-compose-up
```

The command uses the etcd client and server images built from step 1.

The client will continuously check the health of the etcd nodes and print logs similar to:

```
[+] Running 4/4
 ✔ Container etcd0   Created                                                                                                                                                 0.0s 
 ✔ Container etcd2   Created                                                                                                                                                 0.0s 
 ✔ Container etcd1   Created                                                                                                                                                 0.0s 
 ✔ Container client  Recreated                                                                                                                                               0.1s 
Attaching to client, etcd0, etcd1, etcd2
etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.134294Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_ADVERTISE_CLIENT_URLS","variable-value":"http://etcd2.etcd:2379"}
etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.138501Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_INITIAL_ADVERTISE_PEER_URLS","variable-value":"http://etcd2:2380"}
etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.138646Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_INITIAL_CLUSTER","variable-value":"etcd0=http://etcd0:2380,etcd1=http://etcd1:2380,etcd2=http://etcd2:2380"}
etcd0   | {"level":"info","ts":"2025-04-14T07:23:25.138434Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_ADVERTISE_CLIENT_URLS","variable-value":"http://etcd0.etcd:2379"}
etcd0   | {"level":"info","ts":"2025-04-14T07:23:25.138582Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_INITIAL_ADVERTISE_PEER_URLS","variable-value":"http://etcd0:2380"}
etcd0   | {"level":"info","ts":"2025-04-14T07:23:25.138592Z","caller":"flags/flag.go:113","msg":"recognized and used environment variable","variable-name":"ETCD_INITIAL_CLUSTER","variable-value":"etcd0=http://etcd0:2380,etcd1=http://etcd1:2380,etcd2=http://etcd2:2380"}

...
...
(skipping some repeated logs for brevity)
...
...

etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.484698Z","caller":"etcdmain/main.go:50","msg":"successfully notified init daemon"}
etcd1   | {"level":"info","ts":"2025-04-14T07:23:25.484092Z","caller":"embed/serve.go:210","msg":"serving client traffic insecurely; this is strongly discouraged!","traffic":"grpc+http","address":"[::]:2379"}
etcd0   | {"level":"info","ts":"2025-04-14T07:23:25.484563Z","caller":"etcdmain/main.go:50","msg":"successfully notified init daemon"}
etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.485101Z","caller":"v3rpc/health.go:61","msg":"grpc service status changed","service":"","status":"SERVING"}
etcd1   | {"level":"info","ts":"2025-04-14T07:23:25.484130Z","caller":"etcdmain/main.go:44","msg":"notifying init daemon"}
etcd2   | {"level":"info","ts":"2025-04-14T07:23:25.485782Z","caller":"embed/serve.go:210","msg":"serving client traffic insecurely; this is strongly discouraged!","traffic":"grpc+http","address":"[::]:2379"}
etcd1   | {"level":"info","ts":"2025-04-14T07:23:25.484198Z","caller":"etcdmain/main.go:50","msg":"successfully notified init daemon"}
client  | Client [entrypoint]: starting...
client  | Client [entrypoint]: checking cluster health...
client  | Client [entrypoint]: connection successful with etcd0
client  | Client [entrypoint]: connection successful with etcd1
client  | Client [entrypoint]: connection successful with etcd2
client  | Client [entrypoint]: cluster is healthy!
```

And it will stay running indefinitely.

### 4. Running the tests

```bash
make antithesis-run-container-traffic
make antithesis-run-container-validation
```

Alternatively, with the etcd cluster from step 3, to run the tests locally without rebuilding the client image:

```bash
make antithesis-run-local-traffic
make antithesis-run-local-validation
```

### 5. Prepare for next run

Unfortunatelly robustness tests don't support running on non empty database.
So for now you need to cleanup the storage before repeating the run or you will get "non empty database at start, required by model used for linearizability validation" error.

```bash
make antithesis-clean
```

## Troubleshooting

- **Image Pull Errors**: If Docker can’t pull `etcd-client:latest`, make sure you built it locally (see the “Build and Tag” step) or push it to a registry that Compose can access.
