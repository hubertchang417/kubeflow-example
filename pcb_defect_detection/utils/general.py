import os
import numpy as np
import requests
# import cv2
import time
import subprocess
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
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

# class PCB_PostProc:
#     def __init__(self, requests: requests.models.Response, img_path: str, img_size: int = 640):
#         if requests.status_code != 200:
#             raise ValueError(f"Please check your data. err: {requests.json()}")
        
#         if not os.path.exists(img_path):
#             raise ValueError("Image path does not exist.")
        
#         self._img_path = img_path
#         self._img_size = img_size
#         self._labels = ['Spurious Copper', 'Mouse Bite', 'Open Circuit', 'Missing Hole', 'Spur', 'Short']
#         self._colors = [(255, 102, 102), (255, 178, 102), (255, 255, 102), (102, 255, 178), (102, 178, 255), (255,102,255)]
        
#         tmp_pred = requests.json()['data']['ndarray'][0][0]
#         ## post processing prediction result
#         pred_keys = list(tmp_pred.keys())
#         ## (box, conf, cls)
#         self._pred = list((tmp_pred[pred_keys[0]][i],tmp_pred[pred_keys[1]][i],tmp_pred[pred_keys[2]][i]) for i in range(len(tmp_pred[pred_keys[0]])))
#         self._pred_cnt = tmp_pred[pred_keys[3]]

#     def show(self, confidence: float = 0.5, save_path: str = None):
#         image = cv2.imread(self._img_path)
#         img_height, img_width = self._img_size, self._img_size

#         # extend image width
#         bar_width = 250
#         new_width = img_width + bar_width
#         modify_image = np.ones((img_height, new_width, 3), dtype=np.uint8) * 220 # light gray background
#         modify_image[:, :img_width] = image
        
#         for i in range(self._pred_cnt):
#             box, conf, cls = self._pred[i]
#             x_min, y_min, x_max, y_max = box
#             ## rescale
#             x_min = int(x_min * self._img_size)
#             y_min = int(y_min * self._img_size)
#             x_max = int(x_max * self._img_size)
#             y_max = int(y_max * self._img_size)

#             color = self._colors[int(cls)]
            
#             if conf >= confidence:
#                 cv2.rectangle(modify_image, (x_min, y_min), (x_max, y_max), color, 2)
                
#                 # add label
#                 label = self._labels[int(cls)]
#                 label_strs = f"{label}: {conf:.2f}"
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 font_scale = 0.8
#                 font_thickness = 2
#                 text_size, bottom_y = cv2.getTextSize(label_strs, font, font_scale, font_thickness)
                
#                 text_x_max = min(x_min + text_size[0]-10, self._img_size)

#                 cv2.rectangle(modify_image, (text_x_max-text_size[0], y_min-text_size[1]-bottom_y), (text_x_max , y_min), color, -1)
#                 cv2.putText(modify_image, label_strs, (text_x_max-text_size[0], y_min-bottom_y), font, font_scale, (0, 0, 0), font_thickness)
        
#         bar_x_start = img_width + 10  
#         for idx, label in enumerate(self._labels):
#             text_y = 460 + idx * 30  
#             color = self._colors[idx]

#             cv2.rectangle(modify_image, (bar_x_start, text_y - 20), (bar_x_start + 20, text_y), color, -1)
#             cv2.putText(modify_image, label, (bar_x_start + 30, text_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
#         if save_path:
#             cv2.imwrite(save_path, modify_image)
#         else:
#             plt.figure(figsize=(8, 16)) 
#             plt.imshow(modify_image)
#             plt.axis('off') 
#             plt.show()

## PIL version
class PCB_PostProc:
    def __init__(self, requests: requests.models.Response, img_path: str, img_size: int = 640):
        if requests.status_code != 200:
            raise ValueError(f"Please check your data. err: {requests.json()}")
        
        if not os.path.exists(img_path):
            raise ValueError("Image path does not exist.")
        
        self._img_path = img_path
        self._img_size = img_size
        self._labels = ['Spurious Copper', 'Mouse Bite', 'Open Circuit', 'Missing Hole', 'Spur', 'Short']
        self._colors = [(255, 102, 102), (255, 178, 102), (255, 255, 102), (102, 255, 178), (102, 178, 255), (255,102,255)]
        
        tmp_pred = requests.json()['data']['ndarray'][0][0]
        ## post processing prediction result
        pred_keys = list(tmp_pred.keys())
        ## (box, conf, cls)
        self._pred = list((tmp_pred[pred_keys[0]][i],tmp_pred[pred_keys[1]][i],tmp_pred[pred_keys[2]][i]) for i in range(len(tmp_pred[pred_keys[0]])))
        self._pred_cnt = tmp_pred[pred_keys[3]]

    def show(self, confidence: float = 0.5, save_path: str = None):
        # Load the image and convert it to RGB
        image = Image.open(self._img_path).convert("RGB")
        img_height, img_width = self._img_size, self._img_size

        # Extend image width
        bar_width = 250
        new_width = img_width + bar_width
        modify_image = Image.new("RGB", (new_width, img_height), color=(220, 220, 220))  # Light gray background
        modify_image.paste(image, (0, 0))  # Paste the original image on the extended canvas

        # Create a drawing object
        draw = ImageDraw.Draw(modify_image)
        root_dir = os.getcwd()
        if not os.path.exists(f'{root_dir}/fonts/ArimoNerdFont-Bold.ttf'):
            status = self.downloadFonts(root_dir)
            if status:
                raise ValueError("Please download the font from https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/Arimo.zip, and extract in fonts folder")
        font = ImageFont.truetype(f'{root_dir}/fonts/ArimoNerdFont-Bold.ttf', size=12)
        font1 = ImageFont.truetype(f'{root_dir}/fonts/ArimoNerdFont-Bold.ttf', size=24)
        # Draw bounding boxes and labels
        for i in range(self._pred_cnt):
            box, conf, cls = self._pred[i]
            x_min, y_min, x_max, y_max = box
            # Rescale coordinates
            x_min = int(x_min * self._img_size)
            y_min = int(y_min * self._img_size)
            x_max = int(x_max * self._img_size)
            y_max = int(y_max * self._img_size)

            color = self._colors[int(cls)]

            if conf >= confidence:
                # Draw bounding box
                draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=2)

                # Draw label background
                label = self._labels[int(cls)]
                label_strs = f"{label}: {conf:.2f}"
                bbox = draw.textbbox((0, 0), label_strs, font=font)
                text_x_max = min(x_min + bbox[2]+2, self._img_size)

                label_bg_coords = [text_x_max-bbox[2]-4, y_min - bbox[3] - 1, text_x_max, y_min]
                draw.rectangle(label_bg_coords, fill=color)

                # Add label text
                draw.text((text_x_max-bbox[2]-2, y_min - bbox[3] - 1), label_strs, fill=(0, 0, 0), font=font)
                
        # Draw label bar with colors and text
        bar_x_start = img_width + 10
        for idx, label in enumerate(self._labels):
            text_y = 400 + idx * 40
            color = self._colors[idx]
            
            # Draw colored square
            draw.rectangle([bar_x_start, text_y - 20, bar_x_start + 20, text_y], fill=color)
            # Draw label text
            draw.text((bar_x_start + 30, text_y - 20), label, fill=(0, 0, 0), font=font1)

        # Save or display the result
        if save_path:
            modify_image.save(save_path)
        else:
            plt.figure(figsize=(10, 8))
            plt.imshow(modify_image)
            plt.axis("off")
            plt.show()
    def downloadFonts(self, root_dir):
        font_path = f'{root_dir}/fonts/ArimoNerdFont-Bold.ttf'
        
        if not os.path.exists(font_path):

            os.makedirs(f'{root_dir}/fonts', exist_ok=True)
            curl_cmd = ['curl', '-L', '-o', f'{root_dir}/fonts/Arimo.zip', 'https://github.com/ryanoasis/nerd-fonts/releases/download/v3.3.0/Arimo.zip']
            max_chk = 5
            while max_chk >=0:
                try:
                    subprocess.run(curl_cmd, check=True)
                    break
                except subprocess.CalledProcessError as e:
                    print(f"Error during download: {e}")
                    time.sleep(2)
                max_chk-=1
            if os.path.exists(f'{root_dir}/fonts/Arimo.zip'):
                zip_cmd = ['unzip', f'{root_dir}/fonts/Arimo.zip', 'ArimoNerdFont-Bold.ttf', '-d', f'{root_dir}/fonts']
                subprocess.run(zip_cmd, check=True)
                return False
            else:
                return True
            

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
    
    test_img = "<test_img>"
    img = Image.open(test_img)
    img = np.array(img)/255.
    img = img.reshape(-1,640,640,3)
    
    res = sc.predict(img)
    
    post_proc = PCB_PostProc(res, test_img)
    post_proc.show(confidence=0.6)