import os
import numpy as np
import requests
import matplotlib.pyplot as plt
from PIL import Image
# %matplotlib inline

class SeldonCurl:
    def __init__(self, gateway_ep: str = "http://127.0.0.1",  gateway: str = "istio",deploy_name: str = "default", deploy_ns: str = "seldon", auth_token: str = "", cert: str = None):
        self._gateway_ep = gateway_ep
        self._gateway = gateway # istio or default
        self._deploy_name = deploy_name
        self._deploy_ns = deploy_ns
        self._auth_token = auth_token # auth service token
        self._cert = cert # cert path
    
    def predict(self, data): 
        if type(data) == np.ndarray:
            data = {"data": {"ndarray": data.tolist()}}
            if self._cert:
                return requests.post( f'{self.url}/api/v1.0/predictions',headers=self.headers, json=data, verify=self._cert )
            else:
                return requests.post( f'{self.url}/api/v1.0/predictions',headers=self.headers, json=data )
        elif type(data) == list:
            data = {"data": {"ndarray": data}}
            if self._cert:
                return requests.post( f'{self.url}/api/v1.0/predictions',headers=self.headers, json=data, verify=self._cert )
            else:
                return requests.post( f'{self.url}/api/v1.0/predictions',headers=self.headers, json=data )
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    @property
    def headers(self):
        if self._auth_token:
            return {'Content-Type': 'application/json','Cookie': f'authservice_session={self._auth_token}'}
        else:
            return {'Content-Type': 'application/json'}
    
    @property
    def url(self):
        if self._gateway == 'istio':
            return f"{self._gateway_ep}/seldon/{self._deploy_ns}/{self._deploy_name}"
        elif self._gateway == 'default':
            return f"{self._gateway_ep}"
        else:
            raise ValueError(f"Unsupported gateway: {self._gateway}")

class BCS_PostProc:
    def __init__(self, requests: requests.models.Response, test_folder: str):
        if requests.status_code != 200:
            raise ValueError(f"Please check your data. err: {requests.json()}")
        self._requests = requests
        
        tmp_pred = requests.json()['data']['ndarray'][0]
        self._pred = np.array(tmp_pred)

        if not os.path.exists(test_folder):
            raise ValueError("Test folder does not exist.")
        self._test_folder = test_folder


    def show(self ):
        image = Image.open(f'{self._test_folder}/image.png').convert('RGB')
        mask = Image.open(f'{self._test_folder}/mask.png').convert('L')
        pred_mask = (self._pred>0.6).astype('uint8')

        plt.figure(figsize=(10,5))
        plt.subplot(1,3,1)
        plt.title("Original Image")
        plt.imshow(image)
        plt.imshow(mask , cmap='OrRd',alpha=0.4)
        plt.axis('off')

        plt.subplot(1,3,2)
        plt.title("Inference Result")
        plt.imshow(image)
        plt.imshow(pred_mask , cmap='OrRd',alpha=0.4)
        plt.axis('off')

        plt.subplot(1,3,3)
        plt.title("Inference Mask")
        plt.imshow(pred_mask , cmap='gnuplot2')
        plt.axis('off')
        plt.show()

if __name__ == "__main__":


    auth_token = '<auth_token>' # auth service token
    sc = SeldonCurl(
        gateway_ep="<endpoint>", # gateway endpoint
        gateway="istio", # gateway type istio or default
        deploy_name="<deploy_name>", # deploy name
        deploy_ns="<deploy_ns>", # deploy namespace
        auth_token=auth_token,
        cert='<cert_path>' # cert path
    )
    

    # load image
    test_folder = "<test_folder>"
    img = Image.open(f'{test_folder}/image.png')
    img_np = np.array(img)/255.0
    img_np = img_np.reshape(-1,256,256,3)
    res = sc.predict(img_np)
    print(f'Response: {res.status_code}')

    # show result
    postProc = BCS_PostProc(res, test_folder)
    postProc.show()
