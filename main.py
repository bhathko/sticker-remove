from sticker_remover import StickerProcessor

def main():
    # 初始化处理器（这会将 AI 模型加载到内存中）
    processor = StickerProcessor()
    
    # 使用自定义设置处理贴纸
    processor.process(
        input_path="3.jpg", 
        output_path="output_final.png",
        
        # 参数调整指南：
        # ----------------
        # erosion_size: 1 (较小)
        #   - 如果你在边缘看到原图背景的“光晕”，请调大到 2 或 3。
        #   - 如果想保留最多的细节，请设为 0。
        erosion_size=1, 
        
        # island_size: 100
        #   - 如果背景中仍有“灰尘”或“杂点”，请调大。
        #   - 如果角色的细小细节消失了，请调小。
        island_size=100, 
        
        # target_size: (宽度, 高度)
        #   - 这会将结果缩放到指定的像素。
        #   - 角色会保持比例居中显示。
        target_size=(370, 320)
    )

if __name__ == "__main__":
    main()
