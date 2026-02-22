# Geo3D Module

Module tách/gộp texture PNG cho Minecraft 3D models (geo.json).

## Mục đích

Cho phép AI chỉnh sửa màu sắc texture của Minecraft models bằng cách:
1. Tách texture PNG thành nhiều file PXVG nhỏ (dựa vào UV mapping trong geo.json)
2. AI chỉnh sửa các file PXVG
3. Gộp lại thành texture PNG gốc

**LƯU Ý**: Module này CHỈ xử lý texture, KHÔNG tạo hay chỉnh sửa file geo.json.

## Cách dùng

### 1. Tách texture thành PXVG files

```bash
# Mặc định: 1 file per bone (tối ưu, ít file)
pixci geo-split model.geo.json texture.png -o output/

# Chi tiết hơn: 1 file per face (nhiều file hơn)
pixci geo-split model.geo.json texture.png -o output/ --by-face
```

### 2. Chỉnh sửa các file PXVG

Dùng AI hoặc text editor để chỉnh màu trong các file `.pxvg`

### 3. Gộp lại thành texture PNG

```bash
pixci geo-merge output/ model.geo.json -o new_texture.png
```

## Ví dụ thực tế

```bash
# Tách bat texture
pixci geo-split bat.geo.json bat.png -o bat_pxvg/

# Chỉnh màu trong bat_pxvg/*.pxvg
# (Đổi màu nâu thành màu xanh băng)

# Gộp lại
pixci geo-merge bat_pxvg/ bat.geo.json -o bat_winter.png
```

## Cấu trúc file

```
geo3d/
├── __init__.py       # Exports
├── encoder.py        # Tách texture → PXVG
├── decoder.py        # Gộp PXVG → texture
└── README.md         # Docs này
```

## Metadata trong PXVG

Mỗi file PXVG chứa metadata để biết vị trí trong texture atlas:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Model: bat -->
<!-- Bone: body -->
<!-- Cubes: 2 -->
<!-- Face: combined -->
<!-- UV: 0,16,6,12 -->
<pxvg ...>
```

UV format: `x,y,width,height` trong texture atlas.
