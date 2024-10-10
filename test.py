import json
import numpy as np
import os
from argparse import ArgumentParser

def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_rotation_translation_as_npy(shots, output_dir):
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历shots字典，提取rotation和translation，并保存为npy文件
    for image_name, shot_data in shots.items():
        rotation = np.array(shot_data['rotation'])
        translation = np.array(shot_data['translation'])

        # 构造输出文件名，使用图像名称作为文件名
        npy_filename = os.path.join(output_dir, f"{image_name}.npy")
        np.save(npy_filename, {'rotation': rotation, 'translation': translation})
        print(f"Saved {npy_filename}")

    print(f"All images have been processed and saved as .npy files in {output_dir}.")

if __name__ == '__main__':
    parser = ArgumentParser("Get Pose From Json File")
    parser.add_argument("--json_path", default="", type=str)
    parser.add_argument("--output_dir", default="", type=str)
    args = parser.parse_args()

    # JSON文件路径
    json_file_path = args.json_path
    # 读取JSON数据
    json_data = load_json_data(json_file_path)

    # 确保json_data是列表并且每个元素都是字典
    if isinstance(json_data, list):
        # 输出目录
        output_dir = args.output_dir
        for data_dict in json_data:
            # 检查data_dict是否包含'shots'键
            if 'shots' in data_dict:
                shots = data_dict['shots']
                # 提取并保存rotation和translation
                save_rotation_translation_as_npy(shots, output_dir)
            else:
                raise ValueError("JSON data item does not contain 'shots' key")
    else:
        raise ValueError("JSON data is not a list or is empty")