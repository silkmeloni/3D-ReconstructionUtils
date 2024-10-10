import numpy as np
from argparse import ArgumentParser

'''
传入一个.npy文件，查看其内容和格式
'''

parser = ArgumentParser("Colmap converter")
parser.add_argument('-f',"--npy_file_path", default="E:/CG/dataset/quanjingtu/loft/poses/1.jpg_perspective_view_bottom.jpg.npy", type=str)
args = parser.parse_args()
# 指定.npy文件的路径
npy_file_path = args.npy_file_path

# 使用numpy加载.npy文件
array = np.load(npy_file_path, allow_pickle=True)

# 打印数组的内容
print(array)

# 打印数组的形状、数据类型等信息
print("Array shape:", array.shape)
print("Array dtype:", array.dtype)
