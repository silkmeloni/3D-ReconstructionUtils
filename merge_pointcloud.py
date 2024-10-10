import numpy as np
import open3d as o3d
import os
from scipy.spatial.transform import Rotation as R
from argparse import ArgumentParser

'''
python .\merge_pointcloud.py -pose E:\CG\dataset\quanjingtu\loft\poses -pcd E:\CG\dataset\quanjingtu\loft\depth/vit.raft5.large/20241009_154321\pcd\data -o E:\CG\dataset\quanjingtu\loft\merged_point_cloud.ply

'''

'''
Tw = Tw->c * Tc对吧，我现在的点云是Tc，位姿给的应该就是Tw->c(世界坐标系到相机坐标系的变换矩阵)，我想转到世界坐标Tw那确实是直接乘这个变换矩阵就行
'''

#旋转向量转旋转矩阵
def rotation_vector_to_matrix(rotation_vector):
    """
    将旋转向量转换为旋转矩阵（罗德里格斯公式）。

    参数:
    rotation_vector (np.array): 旋转向量。

    返回:
    np.array: 旋转矩阵。
    """
    theta = np.linalg.norm(rotation_vector)
    if theta == 0:
        return np.eye(3)
    k = rotation_vector / theta
    # 计算旋转矩阵
    W = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rotation_matrix = cos_theta * np.eye(3) + (1 - cos_theta) * np.outer(k, k) + sin_theta * W
    return rotation_matrix

#获取poses
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
        print("idx = ", index, "pose_name = ", file_name)
        # 构造poses字典
        poses[index] = {
            'rotation': data['rotation'],
            'translation': data['translation']
        }
    return poses


def load_point_clouds_from_folder(folder_path):
    """
    从指定文件夹加载所有.ply文件，并构造point_clouds字典。
    参数:
    folder_path (str): 包含.ply文件的文件夹路径。
    返回:
    dict: 包含点云对象的point_clouds字典。
    """
    point_clouds = {}
    # 获取文件夹中所有.ply文件，并按文件名排序
    ply_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.ply')])
    for index, file_name in enumerate(ply_files):
        print("idx = ",index,"pcd_name = ",file_name)
        file_path = os.path.join(folder_path, file_name)
        # 读取点云文件
        point_clouds[index] = o3d.io.read_point_cloud(file_path)
    return point_clouds


parser = ArgumentParser("merge pointclouds")
parser.add_argument('-pose',"--pose_folder", default="E:/CG/BiFuse/F1F_Pose", type=str) #E:\CG\dataset\quanjingtu\loft\poses
parser.add_argument('-pcd',"--pcd_folder", default="E:/CG/BiFuse/F1F_Ply", type=str) #E:\CG\dataset\quanjingtu\loft\depth\vit.raft5.large\20241009_154321\pcd\data
parser.add_argument('-o',"--output", default="E:/CG/BiFuse/F1F_Merged/merged_point_cloud.ply", type=str)
parser.add_argument("--start", default="-1", type=int)
parser.add_argument("--end", default="999999", type=int)
args = parser.parse_args()

poses = load_poses_from_npy_folder(args.pose_folder)
point_clouds = load_point_clouds_from_folder(args.pcd_folder)

# 创建一个空的点云对象来存储合并后的点云
merged_point_cloud = o3d.geometry.PointCloud()

# 遍历所有图像的位姿和点云
start = args.start #从1开始
end = args.end

for idx, pose in poses.items():
    if(idx<start-1): #开始
        continue
    if(idx==end): #结束
        break
    pcd = point_clouds[idx]

    # 将归一化的旋转向量转换为旋转矩阵
    print("idx = ",idx,"rot=",pose['rotation'], "tran=",pose['translation'])
    rotation_matrix = rotation_vector_to_matrix(np.array(pose['rotation']))

    # 创建变换矩阵
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = np.array(pose['translation'])
    transformation_matrix = np.linalg.inv(transformation_matrix) #实际上应该用逆矩阵，这是为什么

    # 应用变换矩阵
    pcd.transform(transformation_matrix)

    # 合并点云
    merged_point_cloud += pcd

# 可视化合并后的点云
o3d.visualization.draw_geometries([merged_point_cloud])

# 保存合并后的点云
o3d.io.write_point_cloud(args.output, merged_point_cloud)