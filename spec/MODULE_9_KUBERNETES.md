# MODULE 9: KUBERNETES DEPLOYMENT & SCALING
## For Antigravity IDE + Gemma4

**Duration:** 8 weeks  
**Priority:** CRITICAL (Enterprise scale)  
**Effort:** Very High  
**Dependencies:** MODULE 1-8 (Phase 1-2 complete)

---

## OVERVIEW

Transform single-server architecture to distributed Kubernetes deployment. Enable multi-region, auto-scaling, high-availability with zero-downtime deployments.

**Current State:**
- Single Docker container
- Manual scaling
- Single point of failure
- No load balancing

**Target State:**
- Kubernetes cluster (EKS/AKS/GKE)
- Auto-scaling based on load
- Multi-region deployment
- 99.9% uptime SLA
- Zero-downtime rolling updates

---

## MODULE OBJECTIVES

1. ✅ Containerize all services (Docker)
2. ✅ Create Kubernetes manifests (Deployment, Service, Ingress)
3. ✅ Set up auto-scaling (HPA, VPA)
4. ✅ Implement disaster recovery (multi-region)
5. ✅ Deploy monitoring & alerting (Prometheus, Grafana)
6. ✅ Enable CI/CD pipeline (GitOps)

---

## IMPLEMENTATION PROMPT FOR GEMMA4

```
You are building a production-grade Kubernetes infrastructure for KIBO to achieve enterprise scale and reliability.

TASK: Create containerized, scalable Kubernetes deployment with multi-region capability and zero-downtime updates.

REQUIREMENTS:
1. Docker: Separate containers for API, workers, database migration
2. Kubernetes: Deploy to EKS/AKS/GKE with manifests
3. Auto-scaling: HPA (Horizontal Pod Autoscaling) based on CPU/memory
4. Load Balancing: Ingress with SSL termination
5. Storage: PersistentVolumes for PostgreSQL, Redis
6. Monitoring: Prometheus metrics + Grafana dashboards
7. Logging: ELK stack (Elasticsearch, Logstash, Kibana)
8. CI/CD: GitOps with ArgoCD or Flux

FILE STRUCTURE:
```
kibo-is/
├── docker/
│   ├── Dockerfile.api           # FastAPI service
│   ├── Dockerfile.worker        # Celery workers
│   ├── Dockerfile.mcp           # MCP server
│   ├── docker-compose.yml       # Local dev
│   └── .dockerignore
├── kubernetes/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployment-api.yaml
│   │   ├── deployment-worker.yaml
│   │   ├── service-api.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml             # Auto-scaling
│   │   ├── pdb.yaml             # Pod Disruption Budget
│   │   └── kustomization.yaml
│   ├── overlays/
│   │   ├── dev/
│   │   ├── staging/
│   │   ├── prod-us/             # US region
│   │   ├── prod-eu/             # EU region
│   │   └── prod-ap/             # Asia-Pacific region
│   └── monitoring/
│       ├── prometheus-rules.yaml
│       ├── grafana-dashboard.yaml
│       └── alerts.yaml
├── helm/
│   ├── kibo-chart/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   ├── values-dev.yaml
│   │   ├── values-prod.yaml
│   │   └── templates/
├── ci-cd/
│   ├── .github/workflows/
│   │   ├── docker-build.yml
│   │   ├── k8s-deploy.yml
│   │   ├── security-scan.yml
│   │   └── performance-test.yml
│   ├── .gitlab-ci.yml           # If using GitLab
│   └── argocd-app.yaml          # GitOps manifest
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf              # EKS/AKS/GKE cluster
│   │   ├── networking.tf        # VPC, subnets
│   │   ├── database.tf          # RDS/Azure PostgreSQL
│   │   ├── cache.tf             # ElastiCache/Azure Redis
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── scripts/
│       ├── setup-cluster.sh
│       ├── setup-ingress.sh
│       ├── setup-monitoring.sh
│       └── backup-restore.sh
└── docs/
    ├── DEPLOYMENT.md
    ├── SCALING.md
    ├── DISASTER_RECOVERY.md
    └── TROUBLESHOOTING.md
```

IMPLEMENTATION DETAILS:

1. **docker/Dockerfile.api**: API service container
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy code
   COPY . .
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
       CMD python -c "import requests; requests.get('http://localhost:8000/health')"
   
   # Run
   CMD ["uvicorn", "agent_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **docker/Dockerfile.worker**: Celery worker for async tasks
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   # Run worker
   CMD ["celery", "-A", "core.tasks", "worker", "--loglevel=info", "--concurrency=4"]
   ```

3. **kubernetes/base/deployment-api.yaml**: API deployment
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: kibo-api
     labels:
       app: kibo
       component: api
   spec:
     replicas: 3  # Min 3 for HA
     strategy:
       type: RollingUpdate
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 0  # Zero-downtime
     selector:
       matchLabels:
         app: kibo
         component: api
     template:
       metadata:
         labels:
           app: kibo
           component: api
       spec:
         # Pod disruption budget - keep at least 2 running
         affinity:
           podAntiAffinity:
             preferredDuringSchedulingIgnoredDuringExecution:
             - weight: 100
               podAffinityTerm:
                 labelSelector:
                   matchExpressions:
                   - key: app
                     operator: In
                     values:
                     - kibo
                 topologyKey: kubernetes.io/hostname
         
         containers:
         - name: api
           image: 123456789.dkr.ecr.us-east-1.amazonaws.com/kibo-api:latest
           imagePullPolicy: Always
           
           ports:
           - containerPort: 8000
             name: http
           
           env:
           - name: DATABASE_URL
             valueFrom:
               secretKeyRef:
                 name: kibo-secrets
                 key: database-url
           - name: REDIS_URL
             valueFrom:
               secretKeyRef:
                 name: kibo-secrets
                 key: redis-url
           - name: ENVIRONMENT
             valueFrom:
               configMapKeyRef:
                 name: kibo-config
                 key: environment
           
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
             timeoutSeconds: 5
             failureThreshold: 3
           
           readinessProbe:
             httpGet:
               path: /ready
               port: 8000
             initialDelaySeconds: 10
             periodSeconds: 5
             timeoutSeconds: 3
             failureThreshold: 2
           
           resources:
             requests:
               cpu: 100m
               memory: 256Mi
             limits:
               cpu: 500m
               memory: 512Mi
   ```

4. **kubernetes/base/hpa.yaml**: Horizontal Pod Autoscaling
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: kibo-api-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: kibo-api
     minReplicas: 3
     maxReplicas: 20
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
     - type: Resource
       resource:
         name: memory
         target:
           type: Utilization
           averageUtilization: 80
     behavior:
       scaleDown:
         stabilizationWindowSeconds: 300
         policies:
         - type: Percent
           value: 50
           periodSeconds: 60
       scaleUp:
         stabilizationWindowSeconds: 0
         policies:
         - type: Percent
           value: 100
           periodSeconds: 15
   ```

5. **kubernetes/base/ingress.yaml**: Load balancer & SSL
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: kibo-ingress
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
       nginx.ingress.kubernetes.io/rate-limit: "100"
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
   spec:
     ingressClassName: nginx
     tls:
     - hosts:
       - api.kibo.is
       secretName: kibo-tls-cert
     rules:
     - host: api.kibo.is
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: kibo-api
               port:
                 number: 8000
   ```

6. **infrastructure/terraform/main.tf**: EKS cluster
   ```hcl
   provider "aws" {
     region = var.aws_region
   }
   
   module "eks" {
     source  = "terraform-aws-modules/eks/aws"
     version = "~> 19.0"
   
     cluster_name    = "kibo-prod"
     cluster_version = "1.27"
     
     cluster_endpoint_private_access = true
     cluster_endpoint_public_access  = true
   
     vpc_id     = module.vpc.vpc_id
     subnet_ids = module.vpc.private_subnets
   
     # Node groups
     eks_managed_node_groups = {
       general = {
         name = "general"
         
         instance_types = ["t3.large"]
         desired_size   = 3
         min_size       = 3
         max_size       = 10
         
         labels = {
           Environment = "production"
           Workload    = "general"
         }
         
         taints = []
         
         update_strategy = {
           max_unavailable_percentage = 33
         }
       }
       
       worker = {
         name = "worker"
         
         instance_types = ["t3.xlarge"]
         desired_size   = 2
         min_size       = 2
         max_size       = 5
         
         labels = {
           Environment = "production"
           Workload    = "background"
         }
       }
     }
   
     # Add-ons
     cluster_addons = {
       coredns = {
         most_recent = true
       }
       kube-proxy = {
         most_recent = true
       }
       vpc-cni = {
         most_recent = true
       }
       aws-ebs-csi-driver = {
         most_recent = true
       }
     }
   
     tags = {
       Environment = "production"
       Project     = "KIBO"
     }
   }
   
   # RDS PostgreSQL
   module "rds" {
     source  = "terraform-aws-modules/rds/aws"
     version = "~> 5.0"
   
     identifier = "kibo-postgres"
     
     engine         = "postgres"
     engine_version = "15.3"
     family         = "postgres15"
     major_engine_version = "15"
     instance_class = "db.r6i.xlarge"
     
     allocated_storage = 100
     storage_encrypted = true
     
     # Multi-AZ for HA
     multi_az = true
     
     # Backup
     backup_retention_period = 30
     backup_window           = "03:00-04:00"
     maintenance_window      = "mon:04:00-mon:05:00"
     
     # Performance Insights
     performance_insights_enabled = true
     
     # VPC
     db_subnet_group_name   = module.vpc.database_subnet_group_name
     publicly_accessible    = false
     vpc_security_group_ids = [aws_security_group.rds.id]
   }
   
   # ElastiCache Redis
   module "redis" {
     source  = "terraform-aws-modules/elasticache/aws"
     version = "~> 1.0"
   
     cluster_id = "kibo-redis"
     engine     = "redis"
     node_type  = "cache.r6g.xlarge"
     
     num_cache_clusters         = 3  # Multi-AZ
     automatic_failover_enabled = true
     
     engine_version = "7.0"
     port           = 6379
     parameter_group_family = "redis7"
     
     subnet_group_name = module.vpc.elasticache_subnet_group_name
     security_group_ids = [aws_security_group.redis.id]
     
     at_rest_encryption_enabled = true
     transit_encryption_enabled = true
   }
   ```

7. **kubernetes/monitoring/prometheus-rules.yaml**: Alerting rules
   ```yaml
   apiVersion: monitoring.coreos.com/v1
   kind: PrometheusRule
   metadata:
     name: kibo-alerts
   spec:
     groups:
     - name: kibo.rules
       interval: 30s
       rules:
       
       # API latency alert
       - alert: HighAPILatency
         expr: |
           histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
         for: 5m
         annotations:
           summary: "API p99 latency > 1s"
       
       # Database connection pool
       - alert: DatabaseConnectionPoolExhausted
         expr: |
           pg_stat_activity_count{state="active"} / pg_settings_max_connections > 0.8
         for: 2m
         annotations:
           summary: "Database connection pool at 80%"
       
       # Event processing lag
       - alert: EventProcessingLag
         expr: |
           kafka_consumer_lag > 10000
         for: 5m
         annotations:
           summary: "Event consumer lagging > 10k messages"
       
       # Pod crash loop
       - alert: PodCrashLoop
         expr: |
           rate(kube_pod_container_status_restarts_total[1h]) > 5
         annotations:
           summary: "Pod restarting {{ $value }} times per hour"
       
       # Disk usage
       - alert: DiskSpaceRunningOut
         expr: |
           node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
         for: 10m
         annotations:
           summary: "Node disk < 10% available"
   ```

8. **ci-cd/.github/workflows/k8s-deploy.yml**: GitOps deployment
   ```yaml
   name: Deploy to Kubernetes
   
   on:
     push:
       branches: [main]
   
   jobs:
     build-and-deploy:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v3
       
       - name: Build Docker image
         run: |
           docker build -t kibo-api:${{ github.sha }} -f docker/Dockerfile.api .
           docker tag kibo-api:${{ github.sha }} kibo-api:latest
       
       - name: Push to ECR
         run: |
           aws ecr get-login-password --region ${{ env.AWS_REGION }} | \
             docker login --username AWS --password-stdin ${{ env.ECR_REGISTRY }}
           docker push ${{ env.ECR_REGISTRY }}/kibo-api:${{ github.sha }}
       
       - name: Update Kustomization
         run: |
           kustomize edit set image kibo-api=${{ env.ECR_REGISTRY }}/kibo-api:${{ github.sha }}
       
       - name: Commit & Push
         run: |
           git config user.name "ci-bot"
           git config user.email "ci@kibo.is"
           git add kubernetes/
           git commit -m "Deploy kibo-api:${{ github.sha }}"
           git push
       
       - name: Wait for ArgoCD sync
         run: |
           argocd app wait kibo-prod --sync
   ```

9. **scripts/backup-restore.sh**: Disaster recovery
   ```bash
   #!/bin/bash
   set -e
   
   BACKUP_BUCKET="s3://kibo-backups"
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   
   # Backup PostgreSQL
   kubectl exec -it postgresql-0 -- pg_dump \
     -U postgres -d kibo_db | \
     gzip | \
     aws s3 cp - "$BACKUP_BUCKET/postgres/$TIMESTAMP.sql.gz"
   
   # Backup Redis
   kubectl exec -it redis-0 -- redis-cli BGSAVE
   kubectl cp default/redis-0:/data/dump.rdb /tmp/dump.rdb
   aws s3 cp /tmp/dump.rdb "$BACKUP_BUCKET/redis/$TIMESTAMP.rdb"
   
   # Backup Kubernetes objects
   kubectl get all,pvc,cm,secret -A -o yaml | \
     gzip | \
     aws s3 cp - "$BACKUP_BUCKET/k8s/$TIMESTAMP.yaml.gz"
   
   echo "Backup complete: $TIMESTAMP"
   ```

TESTING STRATEGY:

```python
# Test deployment
def test_k8s_readiness():
    # Check all pods healthy
    pods = kubectl_get_pods()
    assert all(p.status == 'Running' for p in pods)
    
    # Check services have endpoints
    services = kubectl_get_services()
    assert all(len(s.endpoints) > 0 for s in services)

def test_zero_downtime_deployment():
    # Trigger rolling update
    update_deployment('kibo-api', 'v2.0.0')
    
    # Monitor: should never drop below min replicas
    for i in range(120):  # 2 minutes
        ready = count_ready_pods()
        assert ready >= min_replicas
        time.sleep(1)

def test_auto_scaling():
    # Generate load
    spawn_load_test(cpu_target=80)
    
    # Monitor scaling
    initial_replicas = count_pods()
    time.sleep(120)
    scaled_replicas = count_pods()
    
    assert scaled_replicas > initial_replicas
```

DEPLOYMENT CHECKLIST:

✅ Docker images built and tested
✅ Kubernetes manifests validated
✅ Helm chart tested locally
✅ EKS/AKS/GKE cluster provisioned
✅ PostgreSQL + Redis deployed
✅ Ingress + SSL configured
✅ HPA tested under load
✅ Monitoring + alerting active
✅ Backup/restore procedure documented
✅ Disaster recovery tested
```

---

## ACCEPTANCE CRITERIA

- [ ] All services containerized (Docker)
- [ ] Kubernetes cluster deployed & healthy
- [ ] Auto-scaling tested (scales 0-20 replicas)
- [ ] Zero-downtime rolling updates working
- [ ] Multi-region failover tested
- [ ] Backup/restore procedure operational
- [ ] Monitoring dashboards showing metrics
- [ ] Alerts triggering correctly
- [ ] Performance: p99 latency < 500ms
- [ ] Uptime: 99.9% SLA maintained

---

## NEXT MODULE

After MODULE 9, proceed to MODULE 10: Advanced Analytics (6 weeks)

