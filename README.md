# NeuroglancerJsonServer
REST API to serve and store Neuroglancer jsons

# References
```
https://github.com/seung-lab/NeuroglancerJsonServer.git
```

## Installation

Not needed for programmatic access, only for hosting. 

```
git clone https://github.com/seung-lab/NeuroglancerJsonServer.git
cd NeuroglancerJsonServer
pip install . --upgrade
```

## Programmatic access
Using the `requests` package one can post jsons 

```
import requests
json_id = requests.post('{}'.format(server_address), data=[json])
```

and get them

```
import requests
json = requests.get('{}/{}'.format(server_address, json_id))
```


The `requests` package can be installed via

```
pip install requests
```


## 使用CAVEClient进行交互

安装依赖

`pip install caveclient`

需要根据已搭建的json state 后端服务器来更改caveclient的相关参数
```python
from caveclient import  CAVEclient
client = CAVEclient()
state_server = client.state

# 设置json服务器地址以及接口地址
json_server = "http://127.0.0.1:5000"

state_server.default_url_mapping['json_server_address'] = json_server
state_server._endpoints = {'upload_state': '{json_server_address}/nglstate/post',
                           'upload_state_w_id': '{json_server_address}/nglstate/{state_id}',
                           'get_state': '{json_server_address}/nglstate/{state_id}',
                           'get_state_raw': '{json_server_address}/nglstate/raw/{state_id}'}


# 获取sate
url_id = 22
example_state = state_server.get_state_json(url_id)  # dict

# 上传state
new_id = client.state.upload_state_json(example_state)

```


