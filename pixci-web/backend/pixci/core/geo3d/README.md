# Geo3D - Minecraft 3D Model Framework for AI

Framework cho phép AI thiết kế và chỉnh sửa Minecraft/Blockbench 3D models thông qua PXVG format.

## 🎯 Vấn đề

- Texture atlas 64x64 có 500-700 màu khác nhau → File PXVG 1000+ dòng
- AI khó hiểu cấu trúc 3D model phức tạp
- Không thể chỉnh sửa từng bộ phận riêng lẻ

## ✨ Giải pháp

Geo3D tách model 3D thành các **face PXVG nhỏ gọn**:
- Mỗi face = 1 file PXVG độc lập (5x2, 10x8, v.v.)
- Chỉ 8-20 màu per face → File 20-50 dòng
- AI dễ dàng chỉnh sửa màu sắc, thêm chi tiết
- Rebuild lại model 3D từ các face đã chỉnh sửa

## 📦 Cấu trúc Module

```
geo3d/
├── __init__.py       # Public API
├── parser.py         # Parse geo.json files
├── encoder.py        # Encode geo.json → PXVG
├── decoder.py        # Decode PXVG → geo.json
├── canvas3d.py       # High-level 3D modeling API
├── prompts.py        # AI system prompts
└── README.md         # Documentation
```

## 🚀 Quick Start

### 1. Encode Model → PXVG

```bash
# Tách model thành các face PXVG riêng lẻ
pixci geo-encode bowl.geo.json bowl.png -o output/ --mode by_face

# Output:
# output/bowl_bone2_cube0_north.pxvg  (5x2 pixels, 8 colors)
# output/bowl_bone2_cube0_south.pxvg  (5x2 pixels, 8 colors)
# output/bowl_bone2_cube0_east.pxvg   (6x2 pixels, 8 colors)
# ... (12 files total)
```

### 2. AI Chỉnh sửa PXVG

```xml
<!-- bowl_bone2_cube0_east.pxvg -->
<pxvg w="5" h="2">
  <palette>
    <!-- Đổi màu xanh lá sang đỏ -->
    <color k="A" hex="#FF0000FF" />
    <color k="B" hex="#CC0000FF" />
  </palette>
  <layer id="main">
    <dots c="A" pts="1,0 2,0" />
    <dots c="B" pts="3,0 4,0" />
  </layer>
</pxvg>
```

### 3. Rebuild Model

```bash
# Rebuild model từ các PXVG đã chỉnh sửa
pixci geo-decode output/ bowl.geo.json \
  -o bowl_edited.geo.json \
  -t bowl_edited.png \
  --mode by_face
```

## 🎨 Encoding Modes

### `by_face` (Recommended)
- **Mỗi mặt cube = 1 PXVG**
- File nhỏ nhất (20-50 dòng)
- AI dễ chỉnh sửa nhất
- Tốt cho: Đổi màu, thêm chi tiết texture

```bash
pixci geo-encode model.geo.json texture.png -o out/ --mode by_face
```

### `by_cube`
- **Mỗi cube = 1 PXVG** (6 faces combined)
- File trung bình (100-200 dòng)
- Tốt cho: Chỉnh sửa toàn bộ cube

```bash
pixci geo-encode model.geo.json texture.png -o out/ --mode by_cube
```

### `by_bone`
- **Mỗi bone = 1 PXVG** (nhiều cubes)
- File lớn (200-500 dòng)
- Tốt cho: Chỉnh sửa cả bộ phận

```bash
pixci geo-encode model.geo.json texture.png -o out/ --mode by_bone
```

### `single`
- **Toàn bộ model = 1 PXVG**
- File rất lớn (1000+ dòng)
- Không khuyến khích

## 🐍 Python API

### Chỉnh sửa Model có sẵn

```python
from pixci.core.geo3d import encode_geo_to_pxvg, decode_pxvg_to_geo

# Encode
outputs = encode_geo_to_pxvg(
    geo_path="bowl.geo.json",
    texture_path="bowl.png",
    output_dir="pxvg_output/",
    mode="by_face"
)

# AI chỉnh sửa các file PXVG...

# Decode
geo_path, texture_path = decode_pxvg_to_geo(
    pxvg_dir="pxvg_output/",
    original_geo_path="bowl.geo.json",
    output_geo_path="bowl_edited.geo.json",
    output_texture_path="bowl_edited.png",
    mode="by_face"
)
```

### Tạo Model mới từ đầu

```python
from pixci.core.geo3d import Canvas3D

# Khởi tạo model
model = Canvas3D("my_chair", texture_width=64, texture_height=64)

# Tạo bone (bộ phận)
model.add_bone("seat", pivot=(0, 10, 0))

# Thêm cube
model.add_cube(
    origin=(-7, 9, -6),
    size=(14, 2, 12),
    uv_offset=(0, 0)
)

# Tạo chân ghế
model.add_bone("leg_fl", pivot=(-5, 0, -5), parent="seat")
model.add_cube(origin=(-6, 0, -6), size=(2, 9, 2))

model.add_bone("leg_fr", pivot=(5, 0, -5), parent="seat")
model.add_cube(origin=(4, 0, -6), size=(2, 9, 2))

# Lưu
model.save("my_chair.geo.json", "my_chair.png")
```

## 📊 So sánh

| Method | File Size | Colors | AI Difficulty | Use Case |
|--------|-----------|--------|---------------|----------|
| **Full Texture** | 1488 lines | 692 | ❌ Very Hard | N/A |
| **by_face** | 32 lines | 8 | ✅ Easy | Đổi màu, chi tiết |
| **by_cube** | 150 lines | 30 | ⚠️ Medium | Chỉnh sửa cube |
| **by_bone** | 400 lines | 100 | ⚠️ Hard | Chỉnh sửa bone |

## 🎓 Minecraft Geometry Basics

### Coordinate System
- **+X** = Đông (East)
- **+Y** = Lên (Up)
- **+Z** = Nam (South)

### Cube Faces
- **north**: Mặt trước (hướng -Z)
- **south**: Mặt sau (hướng +Z)
- **east**: Mặt phải (hướng +X)
- **west**: Mặt trái (hướng -X)
- **up**: Mặt trên (hướng +Y)
- **down**: Mặt dưới (hướng -Y)

### Bone Hierarchy
```
body (parent)
├── head
├── arm_left
│   └── hand_left
└── arm_right
    └── hand_right
```

### UV Mapping
```
Texture Atlas (64x64):
┌─────────────────┐
│ [face1] [face2] │
│ [face3] [face4] │
│ [face5] [face6] │
└─────────────────┘

UV coordinates: (x, y, width, height)
```

## 🔧 Advanced Usage

### Extract Single Face

```python
from pixci.core.geo3d import GeoModel

model = GeoModel("bowl.geo.json", "bowl.png")
cubes = model.get_all_cubes()

# Get first cube
cube_info = cubes[0]
cube = cube_info['cube_data']
uv = cube['uv']

# Extract north face
face_img = model.extract_face_texture(uv['north'], 'north')
face_img.save("north_face.png")
```

### Custom Face Texture

```python
from PIL import Image
from pixci.core.geo3d import encode_face_to_pxvg

# Create custom texture
face_img = Image.new('RGBA', (8, 8), (255, 0, 0, 255))

# Encode to PXVG
encode_face_to_pxvg(
    face_img,
    "custom_face.pxvg",
    metadata={
        'model': 'custom',
        'bone': 'main',
        'face': 'north'
    }
)
```

## 🤖 AI Integration

### System Prompt
Xem `prompts.py` cho AI system prompts:
- `GEO3D_SYSTEM_PROMPT`: Hướng dẫn tổng quan
- `GEO3D_FACE_EDIT_PROMPT`: Template cho face editing
- `GEO3D_CODE_TEMPLATE`: Template tạo model mới

### Workflow cho AI

1. **Nhận PXVG** với metadata trong comments
2. **Hiểu context**: Model gì? Bone nào? Face nào?
3. **Chỉnh sửa**: Đổi màu trong `<palette>`, thêm chi tiết trong `<layer>`
4. **Giữ nguyên**: Kích thước (w, h), cấu trúc XML
5. **Trả về**: PXVG đã chỉnh sửa

## 📝 Examples

### Example 1: Đổi màu gỗ

```xml
<!-- Before: Nâu -->
<color k="A" hex="#8B4513FF" />

<!-- After: Xanh lá -->
<color k="A" hex="#4A7C59FF" />
```

### Example 2: Thêm pattern

```xml
<layer id="main">
  <!-- Base color -->
  <rect x="0" y="0" w="8" h="8" c="A" />
  
  <!-- Add dots pattern -->
  <dots c="B" pts="1,1 3,1 5,1 7,1 1,3 3,3 5,3 7,3" />
</layer>
```

### Example 3: Gradient

```xml
<layer id="main">
  <row y="0" x1="0" x2="7" c="A" />
  <row y="1" x1="0" x2="7" c="B" />
  <row y="2" x1="0" x2="7" c="C" />
  <row y="3" x1="0" x2="7" c="D" />
</layer>
```

## 🐛 Troubleshooting

### "Texture atlas full"
- Tăng `texture_width` và `texture_height`
- Hoặc tối ưu UV layout

### "Cube not found"
- Kiểm tra `bone_name` và `cube_index`
- Dùng `model.get_all_cubes()` để list

### "UV coordinates out of bounds"
- Kiểm tra UV mapping trong geo.json
- Đảm bảo UV nằm trong (0, 0) → (texture_width, texture_height)

## 📚 References

- [Blockbench Documentation](https://www.blockbench.net/wiki/)
- [Minecraft Bedrock Geometry Format](https://bedrock.dev/docs/stable/Entities#minecraft:geometry)
- [PXVG Specification](../pxvg_engine.py)

## 🎉 Kết luận

Geo3D giúp AI thiết kế 3D models dễ dàng bằng cách:
- ✅ Tách model thành các face nhỏ gọn
- ✅ Giảm complexity từ 1488 dòng → 32 dòng
- ✅ Giảm colors từ 692 → 8 per face
- ✅ Cung cấp high-level API (Canvas3D)
- ✅ Hỗ trợ rebuild model từ PXVG

**Kết quả**: AI có thể chỉnh sửa 3D models như chỉnh sửa pixel art!
