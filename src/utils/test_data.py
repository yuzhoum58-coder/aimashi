"""
合成测试数据 — 用于无DICOM时的开发测试
"""
import numpy as np
from scipy.ndimage import rotate, zoom


def generate_ct_phantom(size: int = 256, num_slices: int = 128) -> np.ndarray:
    """
    生成合成CT体数据 (类似腰椎/骨盆的简化CT体模)
    
    返回 shape=(num_slices, size, size) 的numpy数组
    HU值范围: -1000 (空气) ~ 1500 (骨)
    """
    vol = np.ones((num_slices, size, size), dtype=np.float32) * (-1000)  # 空气背景
    
    cx, cy = size // 2, size // 2
    
    for z in range(num_slices):
        # 椭圆体 (模拟软组织/肌肉轮廓)
        for x in range(size):
            for y in range(size):
                dx = (x - cx) / (size * 0.35)
                dy = (y - cy) / (size * 0.45)
                dz = (z - num_slices//2) / (num_slices * 0.4)
                d = dx*dx + dy*dy + dz*dz
                
                if d < 1.0:
                    vol[z, y, x] = 40  # 软组织HU
                    
                    # 骨结构 (模拟椎体)
                    dx2 = (x - cx) / (size * 0.12)
                    dy2 = (y - cy) / (size * 0.14)
                    dz2 = (z - num_slices//2) / (num_slices * 0.15)
                    d2 = dx2*dx2 + dy2*dy2 + dz2*dz2
                    if d2 < 1.0:
                        vol[z, y, x] = 400  # 松质骨
                    
                    # 皮质骨壳
                    dx3 = (x - cx) / (size * 0.10)
                    dy3 = (y - cy) / (size * 0.12)
                    dz3 = (z - num_slices//2) / (num_slices * 0.13)
                    d3 = dx3*dx3 + dy3*dy3 + dz3*dz3
                    if 0.85 < d3 < 1.0:
                        vol[z, y, x] = 800  # 皮质骨
    
    # 添加椎弓根 (两侧圆形)
    for z in range(num_slices // 3, 2 * num_slices // 3):
        for offset_x in [-size//5, size//5]:
            px = cx + offset_x
            py = cy + size // 4
            for x in range(size):
                for y in range(size):
                    dx = (x - px) / (size * 0.06)
                    dy = (y - py) / (size * 0.06)
                    if dx*dx + dy*dy < 1.0:
                        vol[z, y, x] = 600  # 椎弓根
    
    print(f"✅ CT体模生成: {vol.shape}, HU范围 [{vol.min():.0f}, {vol.max():.0f}]")
    return vol


def generate_mri_phantom(size: int = 256, num_slices: int = 128) -> np.ndarray:
    """
    生成合成MRI体数据 (模拟T2加权)
    
    返回 shape=(num_slices, size, size)
    信号范围: 0~255
    """
    ct = generate_ct_phantom(size, num_slices)
    
    # MRI信号 = 软组织区域高信号 + 骨低信号 + 噪声
    mri = np.zeros_like(ct)
    
    # 软组织区域 (CT值 20~100) → MRI高信号
    soft_mask = (ct > 20) & (ct < 200)
    mri[soft_mask] = 180 + np.random.randn(*soft_mask[soft_mask].shape) * 20
    
    # 骨区域 → MRI低信号 (黑)
    bone_mask = ct >= 200
    mri[bone_mask] = 20 + np.random.randn(*bone_mask[bone_mask].shape) * 10
    
    # 空气 → 无信号
    mri[ct <= -900] = 0
    
    # 添加一些模拟病变/细节
    cx, cy = size // 2, size // 2
    for z in range(num_slices // 3, 2 * num_slices // 3):
        for x in range(size):
            for y in range(size):
                dx = (x - cx - size//10) / (size * 0.03)
                dy = (y - cy - size//10) / (size * 0.03)
                if dx*dx + dy*dy < 1.0:
                    mri[z, y, x] = 250  # 高信号亮点 (模拟神经根/血管)
    
    mri = np.clip(mri, 0, 255).astype(np.float32)
    print(f"✅ MRI体模生成: {mri.shape}, 信号范围 [{mri.min():.0f}, {mri.max():.0f}]")
    return mri


if __name__ == "__main__":
    ct = generate_ct_phantom(128, 64)
    mri = generate_mri_phantom(128, 64)
    print(f"CT: {ct.shape}, {ct.nbytes/1024/1024:.1f}MB")
    print(f"MRI: {mri.shape}, {mri.nbytes/1024/1024:.1f}MB")
