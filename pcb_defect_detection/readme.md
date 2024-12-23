* dataset: https://www.kaggle.com/datasets/akhatova/pcb-defects/data
* kubeflow version: 1.7.0
* kubernetes version: 1.25.6
## prerequisite
1. install kubeflow v1.7.0 (with tls for kubeflow gateway)
   * modify kubeflow/kubeflow-gateway.yaml
    ```
    spec:
    selector:
        istio: ingressgateway
    servers:
        - hosts:
            - '*'
        port:
            name: http
            number: 80
            protocol: HTTP
        tls:
            httpsRedirect: true
        - hosts:
            - '*'
        port:
            name: https
            number: 443
            protocol: HTTPS
        tls:
            mode: SIMPLE
            privateKey: /etc/istio/ingressgateway-certs/tls.key
            serverCertificate: /etc/istio/ingressgateway-certs/tls.crt

    ```
    * add another cert-manager certificate in istio-system namespace
    ```
    apiVersion: cert-manager.io/v1
    kind: Certificate
    metadata:
    name: istio-ingressgateway-certs
    namespace: istio-system
    spec:
    commonName: istio-ingressgateway.istio-system.svc
    dnsNames:
        - istio-ingressgateway.istio-system.svc
        - istio-ingressgateway.istio-system.svc.cluster.local
    ipAddresses:
        - <kubeflow-gateway-loadbalancer-ip> # (optional?)
    isCA: true
    issuerRef:
        kind: ClusterIssuer
        name: kubeflow-self-signing-issuer
    secretName: istio-ingressgateway-certs
    ```
2. install seldon-core v1.17.1 (with istio: kubeflow/kubeflow-gateway)
3. install minio with kubeflow bucket
4. apply prerequisite/seldon-core-rbac.yaml and prerequisite/seldon-core-minio-secret.yaml to kubeflow user namespace
5. get kubeflow gateway tls.crt
6. get kubeflow authservice_session from Cookies (https://awslabs.github.io/kubeflow-manifests/main/docs/component-guides/pipelines/)

## reference
1. [PCB defects detected by YOLO v5](https://www.kaggle.com/code/sunnyconsultant/pcb-defects-detected-by-yolo-v5)
2. [Ultralytic/yolov5](https://github.com/ultralytics/yolov5)
3. [DockerHub - ultralytics/yolov5](https://hub.docker.com/r/ultralytics/yolov5)