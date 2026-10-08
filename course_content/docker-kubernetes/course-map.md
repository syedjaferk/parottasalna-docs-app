# Course map

50 live sessions in 9 phases, on Tuesdays and Thursdays. The journey: understand how containers
really work, master Docker, then learn Kubernetes all the way to deploying a production AI Agent
platform as your final project.

## 📺 Videos so far

The notes follow the [Kube Engineering playlist](https://www.youtube.com/playlist?list=PLMtFsmo8jrN8),
one chapter per episode:

| Episode | Chapter |
|---|---|
| 1 | [Introduction to Docker and its need](sessions/01-why-docker.md) |
| 2 | [Core Linux prerequisites: processes, PIDs, mounts, signals](sessions/02-linux-prerequisites.md) |
| 3 | [File permissions, bind mounts & Docker architecture](sessions/03-permissions-bind-mounts-architecture.md) |
| 4 | [Your first Docker commands](sessions/04-docker-commands.md) |
| 5 | [IP addressing & subnetting](sessions/05-ip-addressing-subnets.md) |
| 6 | [Docker networking: bridge, host, none & overlay](sessions/06-docker-networking.md) |
| 7 | [Master the Dockerfile from scratch](sessions/07-dockerfile.md) |

## The full syllabus

**Legend:** ✅ covered (in a chapter or an *Under the hood* page) · 🟡 partly covered · ⏳ upcoming

## 🟢 Phase 1 · Docker & container fundamentals

| # | Session | Status |
|---|---|---|
| 1 | [Why Docker? Bare metal vs VMs vs containers, portability](sessions/01-why-docker.md) | ✅ |
| 2 | Core Linux prerequisites: processes, PID, mounts, permissions, signals & /proc · [Ch 2](sessions/02-linux-prerequisites.md), [Ch 3](sessions/03-permissions-bind-mounts-architecture.md) | ✅ |
| 3 | [Container isolation: PID, NET, MNT, UTS, USER namespaces](deep-dives/namespaces.md) | ✅ |
| 4 | [Control groups: cgroups v1/v2, CPU/memory limits & the OOM killer](deep-dives/cgroups.md) | ✅ |
| 5 | [Container runtime internals: OCI specs, runc, containerd, Docker Engine vs CRI](deep-dives/container-runtimes.md) | ✅ |

## 🐳 Phase 2 · Docker mastery & workload packaging

| # | Session | Status |
|---|---|---|
| 6 | Docker architecture & CLI: daemon, client, Docker Hub & lifecycle commands · [Ch 3](sessions/03-permissions-bind-mounts-architecture.md), [Ch 4](sessions/04-docker-commands.md) | ✅ |
| 7 | [Docker image mechanics: storage drivers, layering, image IDs, digests & immutability](deep-dives/image-mechanics.md) | ✅ |
| 8 | [Dockerfile fundamentals: FROM, RUN, COPY, ADD, WORKDIR, ENV, CMD vs ENTRYPOINT](sessions/07-dockerfile.md) | ✅ |
| 9 | [Dockerfile deep dive: exec vs shell form, build context, .dockerignore & layer caching](sessions/07-dockerfile.md) | ✅ |
| 10 | Image optimization: Alpine vs distroless vs slim, Dive, Trivy scanning | ⏳ |
| 11 | [Multi-stage builds](sessions/07-dockerfile.md) | 🟡 |
| 12 | Container lifecycle & signal handling: PID 1, graceful shutdowns with FastAPI/Uvicorn | ⏳ |
| 13 | Docker networking fundamentals: bridge, host, none, veth pairs & NAT port mapping · [Ch 5](sessions/05-ip-addressing-subnets.md), [Ch 6](sessions/06-docker-networking.md) | ✅ |
| 14 | [Docker networking deep dive: overlay, macvlan, custom networks & DNS](sessions/06-docker-networking.md) | 🟡 |
| 15 | Docker volumes & persistence: writable layer vs volumes vs bind mounts vs tmpfs | ⏳ |

## 🔵 Phase 3 · Docker Compose, security & observability

| # | Session | Status |
|---|---|---|
| 16 | Docker Compose orchestration: FastAPI + PostgreSQL + Redis + Celery | ⏳ |
| 17 | Advanced Compose: healthchecks, dependencies, secrets, profiles & limits | ⏳ |
| 18 | Container security: rootless, capabilities, seccomp, AppArmor, read-only FS | ⏳ |
| 19 | Container observability: Prometheus, Grafana & cAdvisor | ⏳ |
| 20 | ⚡ Mini-project lab: build & secure a production Docker stack | ⏳ |

## 🟣 Phase 4 · Kubernetes architecture & core primitives

| # | Session | Status |
|---|---|---|
| 21 | Why Kubernetes? Container sprawl & control-plane goals | ⏳ |
| 22 | Architecture: API server, etcd, scheduler, controller manager, kubelet | ⏳ |
| 23 | Installation & setup: Minikube, Kind, K3s, kubeadm, EKS/GKE | ⏳ |
| 24 | Kubernetes API & kubectl: declarative YAML, selectors & labels | ⏳ |
| 25 | Pod mechanics & patterns: pause container, sidecar, ambassador, adapter | ⏳ |
| 26 | Deployments & ReplicaSets: reconciliation, rolling updates, rollbacks | ⏳ |
| 27 | Services: ClusterIP, NodePort, LoadBalancer & endpoints | ⏳ |
| 28 | CoreDNS & service discovery | ⏳ |
| 29 | ConfigMaps & Secrets | ⏳ |
| 30 | Health probes: liveness, readiness & startup | ⏳ |

## 🟠 Phase 5 · Kubernetes networking & storage

| # | Session | Status |
|---|---|---|
| 31 | Networking model: pod, node & service networks | ⏳ |
| 32 | CNI plugins & eBPF: Calico, Cilium, Flannel | ⏳ |
| 33 | Network policies & microsegmentation | ⏳ |
| 34 | Ingress controllers: NGINX, Traefik, TLS termination | ⏳ |
| 35 | Gateway API: Gateway, GatewayClass, HTTPRoute | ⏳ |
| 36 | Storage: emptyDir, hostPath, PV, PVC & StorageClasses | ⏳ |
| 37 | StatefulSets & headless services | ⏳ |
| 38 | DaemonSets, Jobs & CronJobs | ⏳ |

## 🔴 Phase 6 · Scheduling, resources & autoscaling

| # | Session | Status |
|---|---|---|
| 39 | Advanced scheduling: nodeSelector, affinity & anti-affinity | ⏳ |
| 40 | Resource management: requests, limits, QoS classes, LimitRanges | ⏳ |
| 41 | Taints & tolerations: dedicated pools & GPU workloads | ⏳ |
| 42 | Autoscaling: HPA, VPA, Cluster Autoscaler & custom metrics | ⏳ |

## 🛡️ Phase 7 · Cluster security & access control

| # | Session | Status |
|---|---|---|
| 43 | Security model: authentication, authorization, admission controllers | ⏳ |
| 44 | RBAC deep dive: Roles, ClusterRoles, bindings & ServiceAccounts | ⏳ |

## 🟡 Phase 8 · Advanced extensions & operations

| # | Session | Status |
|---|---|---|
| 45 | Helm: charts, templates, values, hooks & releases | ⏳ |
| 46 | CRDs & operators | ⏳ |
| 47 | Full observability stack: Prometheus, Grafana, Loki, FluentBit, OpenTelemetry | ⏳ |
| 48 | 🛠️ Cluster break & fix lab: CrashLoopBackOff, OOMKilled, CNI & PVC issues | ⏳ |

## 🏆 Phase 9 · Production Kubernetes & AI Agent capstone

| # | Session | Status |
|---|---|---|
| 49 | Production HA & GitOps: multi-AZ control plane, etcd backups, Argo CD, canary | ⏳ |
| 50 | 🚀 Final capstone: deploy a production AI Agent platform on Kubernetes | ⏳ |

**The capstone stack:** an AI Agent API (FastAPI with autoscaling), Celery workers with a Redis
queue, a vector database (Qdrant or pgvector), PostgreSQL as a StatefulSet, Gateway API with
automatic TLS, Argo CD for GitOps, and Prometheus, Loki and Grafana for observability.
