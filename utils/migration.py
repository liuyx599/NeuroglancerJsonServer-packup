import json


def convert_layer(layer_obj):
    # 检查每个图层对象的"type"属性和"source"属性来确定是否需要进行转换。
    # 如果图层的"type"是"segmentation"并且"source"属性以特定的前缀开头，那么将"source"属性的值修改为指定的新值，并且如果图层对象中存在"chunkedGraph"属性，则将其删除。
    if layer_obj["type"] == 'segmentation' and "source" in layer_obj:
        if layer_obj['source'].startswith("precomputed://gs://neuroglancer/nkem/pinky100_v0/ws/lost_no-random/bbox1_0"):
            layer_obj['source'] = "graphene://https://www.dynamicannotationframework.com/segmentation/1.0/pinky100_sv16"
            if 'chunkedGraph' in layer_obj:
                del layer_obj['chunkedGraph']


def convert_precomputed_to_graphene_v1(json_data):
    if not isinstance(json_data, dict):
        # 从客户端接收到的其实是byte类型
        j = json.loads(json_data)  # 只要不是dict 类型 通通用loads解码为 dict类型
    else:
        j = json_data

    print(j)
    layers = j["layers"]

    if isinstance(layers, list):
        for layer in layers:
            convert_layer(layer)
    else:
        for l in layers.keys():
            convert_layer(layers[l])

    return json.dumps(j)  # 并通过json.dumps()会将dict转换为str


