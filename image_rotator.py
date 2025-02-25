import os
import random
import string
from PIL import Image
import uuid
import shutil
from typing import List, Tuple

class ImageProcessor:
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        
    def process_image(self, input_path: str, output_dir: str, index: int,
                     rotate: bool = True, scale: bool = False, crop: bool = False,
                     scale_range: Tuple[float, float] = (0.8, 1.5),  # 默认放大为主
                     crop_ratio: float = 0.8) -> Tuple[dict, str]:
        """
        处理单张图片，支持旋转、缩放和裁剪
        
        参数:
        input_path: 输入图片路径
        output_dir: 输出目录
        index: 版本索引
        rotate: 是否启用旋转
        scale: 是否启用缩放
        crop: 是否启用裁剪
        scale_range: 缩放范围 (最小比例, 最大比例)
        crop_ratio: 裁剪保留比例
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        try:
            with Image.open(input_path) as img:
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                original_size = img.size
                processed_img = img.copy()
                modifications = {}
                
                # 组合变换 - 缩放和旋转通常一起使用效果更好
                if scale:
                    # 偏向于放大的缩放因子
                    scale_factor = random.uniform(scale_range[0], scale_range[1])
                    new_size = tuple(int(dim * scale_factor) for dim in processed_img.size)
                    # 兼容旧版本和新版本的PIL库
                    try:
                        processed_img = processed_img.resize(new_size, Image.Resampling.BICUBIC)
                    except AttributeError:
                        # 针对旧版本PIL的修复
                        processed_img = processed_img.resize(new_size, Image.BICUBIC)
                    modifications['scale'] = scale_factor
                
                # 随机旋转
                if rotate:
                    angle = random.uniform(0, 360)
                    # 兼容旧版本和新版本的PIL库
                    try:
                        processed_img = processed_img.rotate(angle, expand=True, 
                                                           resample=Image.Resampling.BICUBIC)
                    except AttributeError:
                        # 针对旧版本PIL的修复
                        processed_img = processed_img.rotate(angle, expand=True, 
                                                           resample=Image.BICUBIC)
                    modifications['rotation'] = angle
                
                # 随机裁剪
                if crop:
                    w, h = processed_img.size
                    crop_w = int(w * crop_ratio)
                    crop_h = int(h * crop_ratio)
                    
                    # 确保有足够的边缘可以裁剪
                    if w > crop_w and h > crop_h:
                        left = random.randint(0, w - crop_w)
                        top = random.randint(0, h - crop_h)
                        processed_img = processed_img.crop((left, top, 
                                                          left + crop_w, 
                                                          top + crop_h))
                        modifications['crop'] = (left, top, left + crop_w, top + crop_h)
                    else:
                        print(f"警告: 图片尺寸过小，跳过裁剪操作 ({w}x{h})")
                
                # 生成输出文件名
                original_name = os.path.splitext(os.path.basename(input_path))[0]
                random_id = str(uuid.uuid4())[:4]
                output_name = f"{original_name}_{random_id}_v{index+1}.jpg"
                output_path = os.path.join(output_dir, output_name)
                
                # 保存处理后的图片
                processed_img.save(output_path, 'JPEG', quality=95)
                return modifications, output_path
                
        except Exception as e:
            print(f"处理图片时出错: {str(e)}")
            return None, None

    def process_multiple_images(self, input_dir: str, base_output_dir: str,
                              num_variations: int, operations: List[str],
                              train_ratio: float = 0.8):
        """
        处理多张图片并按比例分配到训练集和验证集
        
        参数:
        input_dir: 输入目录
        base_output_dir: 基础输出目录
        num_variations: 每张图片的变体数量
        operations: 要执行的操作列表 ['rotate', 'scale', 'crop']
        train_ratio: 训练集比例
        """
        # 创建训练集和验证集目录
        train_dir = os.path.join(base_output_dir, 'train')
        val_dir = os.path.join(base_output_dir, 'val')
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(val_dir, exist_ok=True)
        
        # 获取所有图片文件
        image_files = [f for f in os.listdir(input_dir) 
                      if os.path.splitext(f)[1].lower() in self.supported_formats]
        
        if not image_files:
            print("错误：所选文件夹中没有支持的图片文件！")
            return
            
        total_images = len(image_files)
        total_variations = total_images * num_variations
        processed_count = 0
        
        print(f"\n开始处理 {total_images} 张图片，每张生成 {num_variations} 个版本...")
        print(f"总共将生成 {total_variations} 个文件\n")
        print(f"启用的操作: {', '.join(operations)}\n")
        
        # 确定每张图片的训练集和验证集分配
        train_count = int(num_variations * train_ratio)
        
        for filename in image_files:
            input_path = os.path.join(input_dir, filename)
            print(f"\n处理图片: {filename}")
            
            for i in range(num_variations):
                # 决定当前版本是否为训练集
                is_train = i < train_count
                output_dir = train_dir if is_train else val_dir
                
                # 对每个变体使用随机组合的增强操作
                current_operations = []
                if 'rotate' in operations:
                    current_operations.append('rotate')
                if 'scale' in operations:
                    current_operations.append('scale')
                if 'crop' in operations and len(current_operations) > 0:  # 裁剪通常与其他操作结合
                    current_operations.append('crop')
                
                # 确保至少有一个操作被选中
                if not current_operations and operations:
                    current_operations = [random.choice(operations)]
                
                modifications, output_path = self.process_image(
                    input_path, output_dir, i,
                    rotate='rotate' in current_operations,
                    scale='scale' in current_operations,
                    crop='crop' in current_operations
                )
                
                if modifications:
                    processed_count += 1
                    mod_str = ', '.join([f"{k}: {v}" for k, v in modifications.items()])
                    print(f"版本 {i+1:2d}/{num_variations}: {mod_str} -> {os.path.basename(output_path)}")
                    print(f"保存到: {'训练集' if is_train else '验证集'}")
                    
                    progress = (processed_count / total_variations) * 100
                    print(f"\r总进度: {progress:.1f}%", end="")
        
        print(f"\n\n处理完成！共生成 {processed_count} 个文件")
        print(f"训练集目录: {train_dir}")
        print(f"验证集目录: {val_dir}")

def main():
    processor = ImageProcessor()
    
    print("图片数据增强工具 - 支持旋转、缩放和裁剪")
    print("=" * 50)
    print("支持的图片格式: JPG, JPEG, PNG, BMP, TIFF")
    print("输出格式统一为JPG")
    print("=" * 50)
    
    # 获取输入目录
    while True:
        input_dir = input("\n请输入原始图片所在文件夹的完整路径：").strip()
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            break
        print("错误：无效的文件夹路径，请重新输入")
    
    # 获取输出目录
    while True:
        output_dir = input("\n请输入保存处理后图片的文件夹路径：").strip()
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            break
        except Exception as e:
            print(f"错误：无法创建输出文件夹，请重新输入\n{str(e)}")
    
    # 选择操作
    print("\n请选择要执行的操作（多选）：")
    print("1. 旋转")
    print("2. 缩放 (主要是放大)")
    print("3. 裁剪")
    
    while True:
        try:
            choices = input("请输入选项编号（用空格分隔，如：1 2 3）：").strip().split()
            operations = []
            if '1' in choices: operations.append('rotate')
            if '2' in choices: operations.append('scale')
            if '3' in choices: operations.append('crop')
            if operations:
                break
            print("错误：至少需要选择一个操作")
        except ValueError:
            print("错误：请输入有效的选项")
    
    # 获取变体数量
    while True:
        try:
            num_variations = int(input("\n请输入每张图片需要生成的版本数量："))
            if num_variations > 0:
                break
            print("错误：数量必须大于0，请重新输入")
        except ValueError:
            print("错误：请输入有效的数字")
    
    # 处理图片
    processor.process_multiple_images(input_dir, output_dir, num_variations, operations)
    
    input("\n按Enter键退出程序...")

if __name__ == "__main__":
    main()
