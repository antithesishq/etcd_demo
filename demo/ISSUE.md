<!-- DEMO ARTIFACT — paste into a new GitHub issue on antithesishq/etcd_demo.
     Mirrors upstream etcd-io/etcd#20418 ("Stale reads caused by process pausing").
     Replace the /cc handles before opening. -->

### Bug report criteria

- [ ] This bug report is not security related, security issues should be disclosed privately via security@etcd.io.
- [ ] This is not a support request or question, support requests or questions should be raised in the etcd [discussion forums](https://github.com/etcd-io/etcd/discussions).
- [ ] You have read the etcd [bug reporting guidelines](https://github.com/etcd-io/etcd/blob/main/Documentation/contributor-guide/reporting_bugs.md).
- [ ] Existing open issues along with etcd [frequently asked questions](https://etcd.io/docs/latest/faq) have been checked and this is not a duplicate.

### What happened?

Looks like one member's revision has not progressed for a long time, but it still accepted reads and writes — a stale read that breaks linearizability.

Antithesis flagged it: the `Linearization validation passes` always-assertion failed with **108 counterexamples** in a single run.

Antithesis report: https://public.antithesis.com/report/3CY4I__FQwDpo9zAvf_pUdQf/9k0Kgffv58q_dBPp2zaa2UiPhHUMriTQsozQC7b4Ow4.html (run `517ea7809cf80d9abbbe69c10638bd78-55-12`)


### What did you expect to happen?

No linearization issues.

### How can we reproduce it (as minimally and precisely as possible)?

Run the etcd Antithesis setup against etcd **v3.6.3** with process pausing enabled. The robustness validator reports `Linearization illegal`.


### Etcd version (please run commands below)

```
v3.6.3 (git-sha 1ed440d)
```

### Etcd configuration (command line flags or environment variables)

```
ETCD_SNAPSHOT_CATCHUP_ENTRIES: 100
ETCD_SNAPSHOT_COUNT: 50
ETCD_COMPACTION_BATCH_LIMIT: 10
```

### Etcd debug information (please run commands below, feel free to obfuscate the IP address or FQDN in the output)

<details>

```console
$ etcdctl member list -w table
$ etcdctl --endpoints=<member list> endpoint status -w table
```

</details>

### Relevant log output

```Shell
{"level":"error","caller":"validate/operations.go:78","msg":"Linearization illegal"}
{"level":"info","caller":"validate/validate.go:49","msg":"Skipping other validations as linearization failed"}
```
