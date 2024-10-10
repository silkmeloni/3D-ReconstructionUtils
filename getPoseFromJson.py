'''
指令：
python .\tools\getPoseFromJson.py --json_path E:\CG\BiFuse\reconstruction.json --output_dir E:\CG\BiFuse\F1F_Pose\

OpenSfM环节会生成reconstruction.json文件，里面有每张图片位姿，将其旋转向量(1*3)和位移向量(1*3)写入.npy文件
之后可通过np.array(pose['rotation']) 和 np.array(pose['translation'])得到


def load_poses_from_npy_folder(folder_path):
    """
    从指定文件夹加载所有.npy文件，并构造poses字典。
    参数:
    folder_path (str): 包含.npy文件的文件夹路径。
    返回:
    dict: 包含rotation和translation信息的poses字典。
    """
    poses = {}
    # 获取文件夹中所有.npy文件，并按文件名排序
    npy_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.npy')])
    for index, file_name in enumerate(npy_files):
        file_path = os.path.join(folder_path, file_name)
        # 加载.npy文件
        data = np.load(file_path, allow_pickle=True).item()
        # 构造poses字典
        poses[index] = {
            'rotation': data['rotation'],
            'translation': data['translation']
        }
    return poses
'''

import json
import numpy as np
import os
from argparse import ArgumentParser


def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def save_rotation_translation_as_npy(shots, output_dir):
    # 获取所有图像的名称，并按字典序排序
    image_names = sorted(shots.keys())

    # 创建一个目录来存储.npy文件
    os.makedirs(output_dir, exist_ok=True)

    # 遍历图像名称，提取rotation和translation，并保存为npy文件
    for index, image_name in enumerate(image_names,start=1):
        shot_data = shots[image_name]
        rotation = np.array(shot_data['rotation'])
        translation = np.array(shot_data['translation'])
        print("rotation:", rotation)
        print("translation:", translation)

        # 保存为npy文件
        npy_filename = f"{output_dir}/image_{index:03}.npy"
        np.save(npy_filename, {'rotation': rotation, 'translation': translation})
        print(f"Saved {npy_filename}")

    print("All images have been processed and saved as .npy files.")


if __name__ == '__main__':
    parser = ArgumentParser("Get Pose From Json File")
    parser.add_argument("--json_path", default="", type=str)
    parser.add_argument("--output_dir", default="", type=str)
    args = parser.parse_args()

    # JSON文件路径
    json_file_path = args.json_path
    # 读取JSON数据
    json_data = load_json_data(json_file_path)

    # 确保json_data是列表并且至少有一个元素
    if isinstance(json_data, list) and len(json_data) > 0:
        # 获取第一个元素，它应该是包含"cameras"和"shots"的字典
        data_dict = json_data[0]

        # 检查data_dict是否包含'shots'键
        if 'shots' in data_dict:
            shots = data_dict['shots']
        else:
            raise ValueError("JSON data does not contain 'shots' key")

        # 输出目录
        output_dir = 'output_npy_files'

        # 提取并保存rotation和translation
        save_rotation_translation_as_npy(shots, output_dir)
    else:
        raise ValueError("JSON data is not a list or is empty")
    # 输出目录
    output_dir = args.output_dir
    # 提取并保存rotation和translation
    save_rotation_translation_as_npy(shots, output_dir)