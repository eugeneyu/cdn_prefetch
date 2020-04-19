# cdn_prefetch (CDN预热)

A tool to improve file download speed from Google Cloud CDN by pre-fetching hot files from the origin to the CDN cache in the GCP regions, before the clients start downloading them.

The below tests proves the effectiveness of pre-fetching.
以下测试说明预热效果。

 - 文件均存储在印度Bucket
 - 缓存预热是通过GCE实例请求相应文件
 - 文件下载均执行在新加坡EC2

http://35.244.143.158/googlework_short_1.mp4   无预热

curl -v http://35.244.143.158/googlework_short_1.mp4 --output file.mp4

第一次，Edge无缓存
100 1455k  100 1455k    0     0  5578k      0 --:--:-- --:--:-- --:--:-- 5578k

第二次，Edge有缓存
100 1455k  100 1455k    0     0  24.9M      0 --:--:-- --:--:-- --:--:-- 24.9M


http://35.244.143.158/googlework_short_2.mp4   在印度区域预热

curl -v http://35.244.143.158/googlework_short_2.mp4 --output file.mp4

第一次，Edge无缓存
100 1455k  100 1455k    0     0  5687k      0 --:--:-- --:--:-- --:--:-- 5687k

第二次，Edge有缓存
100 1455k  100 1455k    0     0  43.0M      0 --:--:-- --:--:-- --:--:-- 43.0M


http://35.244.143.158/googlework_short_3.mp4   在新加坡区域预热

curl -v http://35.244.143.158/googlework_short_3.mp4 --output file.mp4

第一次，Edge有缓存
100 1455k  100 1455k    0     0  36.4M      0 --:--:-- --:--:-- --:--:-- 37.4M

另外：如果在印度区域预热，从印度EC2访问也可以命中缓存

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

export PROJECT_ID=\$(gcloud config get-value project)   
gcloud builds submit --tag gcr.io/\$PROJECT_ID\/cdn_prefetch:latest  

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

http://&lt;PREFETCH SERVICE IP&gt;/prefetch?url=http://35.244.150.103/image/demo-image.jpg
