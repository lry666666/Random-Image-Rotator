import os
import random
import string
from PIL import Image
import uuid

def rotate_image(input_path, output_dir, index):
    """
    对输入图片进行随机角度旋转并保存
    
    参数:
    input_path: 输入图片的路径
    output_dir: 输出目录路径
    index: 当前是第几个版本(用于文件名)
    """
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开图片
    try:
        with Image.open(input_path) as img:
            # 如果图片是RGBA模式，转换为RGB
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # 获取原始图片尺寸
            original_size = img.size
            
            # 生成随机旋转角度 (0-360度)
            angle = random.uniform(0, 360)
            
            # 旋转图片,扩展画布以适应旋转后的图片
            rotated = img.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
            
            # 计算新尺寸下的中心点
            new_w, new_h = rotated.size
            center_x = new_w // 2
            center_y = new_h // 2
            
            # 计算裁剪区域,使其与原图尺寸相同
            left = center_x - original_size[0] // 2
            top = center_y - original_size[1] // 2
            right = left + original_size[0]
            bottom = top + original_size[1]
            
            # 裁剪图片至原始尺寸
            final_img = rotated.crop((left, top, right, bottom))
            
            # 生成文件名: 原文件名_随机ID_版本号
            original_name = os.path.splitext(os.path.basename(input_path))[0]
            random_id = str(uuid.uuid4())[:4]
            output_name = f"{original_name}_{random_id}_v{index+1}.jpg"
            output_path = os.path.join(output_dir, output_name)
            
            # 保存图片为jpg格式
            final_img.save(output_path, 'JPEG', quality=95)
            return angle, output_path
            
    except Exception as e:
        print(f"处理图片时出错: {str(e)}")
        return None, None

def process_multiple_images(input_dir, output_dir, num_variations):
    """
    处理目录下的所有图片,每张图片生成指定数量的随机旋转版本
    
    参数:
    input_dir: 输入图片目录
    output_dir: 输出目录
    num_variations: 每张图片要生成的变体数量
    """
    
    # 支持的图片格式
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    
    # 获取所有图片文件
    image_files = [f for f in os.listdir(input_dir) 
                  if os.path.splitext(f)[1].lower() in supported_formats]
    
    if not image_files:
        print("错误：所选文件夹中没有支持的图片文件！")
        return
    
    total_images = len(image_files)
    total_variations = total_images * num_variations
    processed_count = 0
    
    print(f"\n开始处理 {total_images} 张图片，每张生成 {num_variations} 个版本...")
    print(f"总共将生成 {total_variations} 个文件\n")
    
    # 遍历处理每张图片
    for filename in image_files:
        input_path = os.path.join(input_dir, filename)
        print(f"\n处理图片: {filename}")
        
        # 为每张图片生成指定数量的随机旋转版本
        for i in range(num_variations):
            angle, output_path = rotate_image(input_path, output_dir, i)
            if angle is not None:
                processed_count += 1
                print(f"版本 {i+1:2d}/{num_variations}: 旋转 {angle:.1f}° -> {os.path.basename(output_path)}")
                
                # 显示进度
                progress = (processed_count / total_variations) * 100
                print(f"\r总进度: {progress:.1f}%", end="")
    
    print(f"\n\n处理完成！共生成 {processed_count} 个文件")
    print(f"输出目录: {output_dir}")

def main():
    """
    主函数：处理用户输入和程序流程
    """
    print("图片随机旋转工具")
    print("=" * 50)
    print("支持的图片格式: JPG, JPEG, PNG, BMP, TIFF")
    print("输出格式统一为JPG")
    print("=" * 50)
    
    # 获取输入文件夹路径
    while True:
        input_dir = input("\n请输入原始图片所在文件夹的完整路径：").strip()
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            break
        print("错误：无效的文件夹路径，请重新输入")
        
    # 获取输出文件夹路径
    while True:
        output_dir = input("\n请输入保存处理后图片的文件夹路径：").strip()
        try:
            # 如果文件夹不存在，尝试创建
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            break
        except Exception as e:
            print(f"错误：无法创建输出文件夹，请重新输入\n{str(e)}")
    
    # 获取需要生成的随机角度版本数量
    while True:
        try:
            num_variations = int(input("\n请输入每张图片需要生成的随机角度版本数量："))
            if num_variations > 0:
                break
            print("错误：数量必须大于0，请重新输入")
        except ValueError:
            print("错误：请输入有效的数字")
    
    # 处理图片
    process_multiple_images(input_dir, output_dir, num_variations)
    
    input("\n按Enter键退出程序...")

if __name__ == "__main__":
    main()