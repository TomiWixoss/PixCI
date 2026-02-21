import pixci

def test_animation():
    anim = pixci.Animation(32, 32, columns=4, fps=5)
    
    # Sử dụng color tuỳ chỉnh thay vì pic-8
    palette = {
        "09": "#6ABE30FF", # Màu xanh lá của thân
        "10": "#37946EFF", # Bóng tối
        "01": "#1A1C2CFF", # Đen của mắt
    }
    anim.add_palette(palette)
    
    # 1. KHU VỰC ĐỊNH NGHĨA
    # Bộ phận 1: Thân con Slime (mặc định)
    slime_body = pixci.Canvas(32, 32)
    slime_body.add_palette(palette)
    slime_body.draw_dome(16, 28, 20, 12, "09")
    slime_body.draw_rows([(28, 6, 26, "10")]) # Bóng mờ dưới đáy
    
    # Bộ phận 1 (biến thể lùn): Thân con Slime
    slime_body_squish = pixci.Canvas(32, 32)
    slime_body_squish.add_palette(palette)
    slime_body_squish.draw_dome(16, 28, 22, 8, "09")
    slime_body_squish.draw_rows([(28, 5, 27, "10")])
    
    # Bộ phận 2: Đôi mắt
    slime_eyes = pixci.Canvas(32, 32)
    slime_eyes.add_palette(palette)
    slime_eyes.fill_rect((12, 20), (13, 22), "01") # w=2, h=3
    slime_eyes.fill_rect((18, 20), (19, 22), "01")
    
    # 2. KHU VỰC ANIMATION
    
    # Frame 1: Trạng thái đứng im
    f1 = anim.add_frame()
    f1.paste(slime_body, (0, 0))
    f1.paste(slime_eyes, (0, 0))
    f1.add_outline(thickness=1, color="#1A1C2C")

    # Frame 2: Nhún xuống chuẩn bị nảy
    f2 = anim.add_frame()
    f2.paste(slime_body_squish, (0, 0))
    f2.paste(slime_eyes, (0, 2))
    f2.add_outline(thickness=1, color="#1A1C2C")

    # Frame 3: Nảy lên không trung
    f3 = anim.add_frame()
    f3.paste(slime_body, (0, -4))
    f3.paste(slime_eyes, (0, -4))
    f3.add_outline(thickness=1, color="#1A1C2C")

    # Frame 4: Rơi xuống (Giống Frame 1 nhưng mắt mở to xíu)
    f4 = anim.add_frame()
    f4.paste(slime_body, (0, 0))
    f4.paste(slime_eyes, (0, 1))
    f4.add_outline(thickness=1, color="#1A1C2C")
    
    anim.save("slime_from_py.png", scale=10)
    print("Done generating slime_from_py.png and slime_from_py.gif")

if __name__ == '__main__':
    test_animation()
