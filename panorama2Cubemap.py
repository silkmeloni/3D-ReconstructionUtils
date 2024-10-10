import argparse
import os
from PIL import Image

def panorama_to_cubemap(pano_path, output_size, output_dir):
    # 打开全景图
    with Image.open(pano_path) as pano:
        # 确保全景图是等矩形的
        pano_width, pano_height = pano.size
        assert pano_width == 2 * pano_height, "全景图必须是等矩形的"

        # 计算每个面的中心点
        center_x = pano_width // 2
        center_y = pano_height // 2

        # 计算每个面的裁剪区域
        crop_width = output_size
        crop_height = output_size

        # 前面 (-90度)
        front = pano.crop((center_x - center_x // 2, center_y - crop_height // 2, center_x - center_x // 2 + crop_width, center_y + crop_height // 2))

        # 后面 (90度)
        back = pano.crop((center_x + center_x // 2, center_y - crop_height // 2, center_x + center_x // 2 + crop_width, center_y + crop_height // 2))

        # 左面 (180度)
        left = pano.crop((center_x - crop_width // 2, center_y - crop_height // 2, center_x + crop_width // 2, center_y + crop_height // 2))

        # 右面 (0度)
        right = pano.crop((center_x + center_x // 2, center_y - crop_height // 2, center_x + center_x // 2 + crop_width, center_y + crop_height // 2))

        # 上面 (270度)
        up = pano.crop((center_x - crop_width // 2, center_y - crop_height // 2, center_x + crop_width // 2, center_y))

        # 下面 (90度)
        down = pano.crop((center_x - crop_width // 2, center_y, center_x + crop_width // 2, center_y + crop_height))

        # 保存六面图
        for face, img in [('front', front), ('back', back), ('left', left), ('right', right), ('up', up), ('down', down)]:
            img.save(os.path.join(output_dir, f'{os.path.basename(pano_path)}_{face}.png'))

def process_directory(input_dir, output_size, output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历输入目录中的所有文件
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.jpg', '.png')):
            pano_path = os.path.join(input_dir, filename)
            print(f"Processing image: {filename}")  # 输出当前处理的图片名称
            panorama_to_cubemap(pano_path, output_size, output_dir)

def main():
    parser = argparse.ArgumentParser(description='Convert all panoramic images in a directory to cubemaps.')
    parser.add_argument('-i','--input_dir', type=str, help='Directory containing panoramic images.')
    parser.add_argument('-s', '--output_size', type=int, default=1024, help='Size of each face of the cubemap.')
    parser.add_argument('-o','--output_dir', type=str, help='Directory to save the cubemap faces.')
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_size, args.output_dir)

if __name__ == '__main__':
    main()