import cv2
import numpy as np
from PIL import Image
from transformers import pipeline
import torch

class StickerProcessor:
    """
    专业的贴纸制作工具。
    包含：背景去除、噪声清理、边缘优化以及高质量缩放功能。
    """
    
    def __init__(self):
        """
        初始化处理器并加载 RMBG-1.4 模型。
        该模型是目前最先进的高精度背景去除模型之一。
        """
        print("正在加载 RMBG-1.4 模型...")
        # 自动检测设备：支持英伟达显卡 (CUDA) 或 苹果 M 系列芯片 (MPS)
        self.pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)

    def process(self, input_path, output_path, erosion_size=1, island_size=50, target_size=None):
        """
        主处理流水线。
        
        参数说明:
        -----------
        input_path (str):   原始图片路径。
        output_path (str):  保存最终 PNG 贴纸的路径。
        
        erosion_size (int): 边缘收缩（解决白边/光晕问题）
                            作用：将贴纸的边缘向内收缩 N 个像素。
                            - 调大（如 2 或 3）：如果你发现边缘还残留有原图背景的颜色（光晕）。
                            - 调小（0）：如果角色尖锐的细节（如发尖）被切掉了。
                            
        island_size (int):  孤岛去除（清理杂点）
                            作用：删除面积小于该值的独立像素块。
                            - 调大（如 200）：如果背景中残留了很多小的“灰尘”或“杂点”。
                            - 调小（如 20）：如果角色身上细小的部分（如漂浮的火花或细发丝）消失了。
                            
        target_size (tuple): 尺寸调整 (宽度, 高度)
                            作用：将贴纸缩放到指定大小（如 370x320）。
                            - 保持宽高比（不会拉伸变形）。
                            - 贴纸会居中放置，其余部分填充透明。
        """
        print(f"正在处理: {input_path}")
        
        # --- 第一步：加载图像 ---
        # 转换为 RGB 模式以确保与神经网络兼容
        image = Image.open(input_path).convert("RGB")
        img_np = np.array(image)
        
        # --- 第二步：背景去除 ---
        # 模型返回一个 RGBA 图像，其中 'A' (Alpha) 通道即为透明遮罩。
        result_rgba = self.pipe(image)
        result_np = np.array(result_rgba)
        
        # 将颜色通道 (RGB) 与 透明通道 (A) 分离
        r, g, b, a = cv2.split(result_np)
        
        # --- 第三步：手术级去噪（孤岛去除） ---
        # 将透明通道转换为黑白二值图，以便识别不相连的区域。
        _, thresh = cv2.threshold(a, 10, 255, cv2.THRESH_BINARY)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(thresh, connectivity=8)
        
        # 遍历所有识别出的物体，仅保留面积大于 'island_size' 的部分
        new_mask = np.zeros_like(a)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > island_size:
                new_mask[labels == i] = 255
        
        # 将清理后的遮罩应用回原始透明通道
        a_cleaned = cv2.bitwise_and(a, new_mask)
        
        # --- 第四步：消除光晕（边缘腐蚀/收缩） ---
        # “切掉”遮罩的边缘，以移除渗入边缘的背景颜色。
        if erosion_size > 0:
            kernel = np.ones((erosion_size + 1, erosion_size + 1), np.uint8)
            a_cleaned = cv2.erode(a_cleaned, kernel, iterations=1)
        
        # --- 第五步：边缘平滑 ---
        # 对遮罩边缘进行轻微模糊，使其看起来不那么“锯齿化”或“生硬”。
        a_cleaned = cv2.GaussianBlur(a_cleaned, (3, 3), 0)

        # --- 第六步：内部去噪（减少颗粒感） ---
        # 使用非局部均值滤波清理角色内部的杂色。
        # 这会让动漫角色的颜色看起来更平滑、更专业。
        clean_rgb = cv2.fastNlMeansDenoisingColored(img_np, None, 5, 5, 7, 21)
        r_c, g_c, b_c = cv2.split(clean_rgb)

        # --- 第七步：合并通道 ---
        # 将清理后的颜色与优化后的透明遮罩合并。
        final_rgba = cv2.merge([r_c, g_c, b_c, a_cleaned])
        result_img = Image.fromarray(final_rgba)

        # --- 第八步：高质量尺寸缩放 ---
        if target_size:
            target_w, target_h = target_size
            # LANCZOS 是高质量缩放的行业标准。
            # .thumbnail() 会完美保持图像的宽高比。
            result_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            
            # 创建一个完全透明的画布，并将贴纸居中粘贴上去。
            new_canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
            offset = ((target_w - result_img.width) // 2, (target_h - result_img.height) // 2)
            new_canvas.paste(result_img, offset)
            result_img = new_canvas
        
        # --- 第九步：保存结果 ---
        result_img.save(output_path)
        print(f"成功！已保存至 {output_path}，尺寸为 {result_img.size}")