# cdn_prefetch

## 创建 GCE deployment
gcloud deployment-manager deployments create cdn-prefetch --config cdn-prefetch-config.yaml

## 删除 GCE deployment

gcloud deployment-manager deployments delete cdn-prefetch

## Build image

gcloud builds submit --tag=‘0.1’ gcr.io/youzhi-lab/cdn_prefetch:0.1 .

## Run K8s deployment with image

kubectl run --replicas=1 --image=gcr.io/youzhi-lab/cdn_prefetch:0.1 prefetch
kubectl label pods prefetch-65994cb6fb-mlkfk 'app=prefetch'

## Run K8s service

kubectl apply -f prefetch-service.yaml
