# cdn_prefetch

## Create SSH key

ssh-keygen -t rsa -f ~/.ssh/prefetch_key -C prefetch  
cat ~/.ssh/prefetch_key.pub  
  
Update cdn_prefetch/multi-instance.jinja line 16 with the displayed public key  

## Create GCE deployment
gcloud deployment-manager deployments create cdn-prefetch --config cdn-prefetch-config.yaml

## Delete GCE deployment (Only run when the service is no longer needed)

gcloud deployment-manager deployments delete cdn-prefetch

## Build image

gcloud compute instances list --filter="name~'cdn-prefetch*'" --format="csv\[no-heading\](name,EXTERNAL_IP)" > nodes.txt  
gcloud builds submit --tag gcr.io/youzhi-lab/cdn_prefetch:0.1 

## Run K8s deployment with image

<!--
kubectl run --replicas=1 --image=gcr.io/youzhi-lab/cdn_prefetch:0.1 --labels="app=prefetch" prefetch  
-->
kubectl create secret generic prefetch-key --from-file ~/.ssh/prefetch_key  

kubectl apply -f prefetch-deployment.yaml

## Run K8s service

kubectl apply -f prefetch-service.yaml  

Run  
kubectl get services prefetch  
Until the external IP is displayed  

## Send CDN prefetch request

http://&lt;PREFETCH SERVICE IP&gt;/prefetch?url=http://34.96.65.189/do_not_delete/test.txt
