# cdn_prefetch

## 创建 GCE deployment
gcloud deployment-manager deployments create cdn-prefetch --config cdn-prefetch-config.yaml

## 删除 GCE deployment

gcloud deployment-manager deployments delete cdn-prefetch

## Build image

gcloud compute instances list --filter="name~'cdn-prefetch*'" --format="csv\[no-heading\](name,EXTERNAL_IP)" > nodes.txt  
gcloud builds submit --tag gcr.io/youzhi-lab/cdn_prefetch:0.1 

## Run K8s deployment with image

kubectl run --replicas=1 --image=gcr.io/youzhi-lab/cdn_prefetch:0.1 --labels="app=prefetch" prefetch  

## Run K8s service

kubectl apply -f prefetch-service.yaml  

Run  
kubectl get services prefetch  
Until the external IP is displayed  

## Send CDN prefetch request

http://&lt;PREFETCH SERVICE IP&gt;/prefetch?url=http://34.96.65.189/do_not_delete/test.txt
