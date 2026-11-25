from PIL import Image, ImageDraw

def generate_ico():
    size = (64, 64)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded dark navy background
    draw.rounded_rectangle([(2, 2), (62, 62)], radius=14, fill=(5, 12, 30, 255), outline=(56, 189, 248, 200), width=2)

    # Stylized aerodynamic sports car body
    car_points = [
        (10, 44), (16, 44), (18, 38), (24, 38), (26, 44),
        (38, 44), (40, 38), (48, 38), (50, 44), (56, 44),
        (58, 38), (54, 32), (46, 28), (38, 20), (28, 20),
        (18, 24), (12, 32), (8, 38)
    ]
    draw.polygon(car_points, fill=(34, 211, 238, 255))

    # Car Cabin Glass
    cabin_points = [(26, 23), (36, 23), (42, 29), (20, 29), (24, 24)]
    draw.polygon(cabin_points, fill=(2, 6, 20, 240))

    # Wheels
    draw.ellipse([(18, 38), (28, 48)], fill=(2, 6, 20, 255), outline=(56, 189, 248, 255), width=2)
    draw.ellipse([(21, 41), (25, 45)], fill=(34, 211, 238, 255))
    draw.ellipse([(42, 38), (52, 48)], fill=(2, 6, 20, 255), outline=(56, 189, 248, 255), width=2)
    draw.ellipse([(45, 41), (49, 45)], fill=(34, 211, 238, 255))

    # AI Electricity / Sentiment Lightning Bolt
    bolt_points = [(36, 8), (26, 22), (32, 22), (28, 34), (40, 18), (34, 18)]
    draw.polygon(bolt_points, fill=(250, 204, 21, 255), outline=(255, 255, 255, 255))

    img.save("frontend/dist/favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("Successfully generated frontend/dist/favicon.ico")

if __name__ == "__main__":
    generate_ico()
