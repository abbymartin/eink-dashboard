def convert(svg_file, png_file):
    from wand.api import library
    import wand.color
    import wand.image

    with open(svg_file, "r") as svg_file:
        with wand.image.Image() as image:
            with wand.color.Color('transparent') as background_color:
                library.MagickSetBackgroundColor(image.wand, 
                                                 background_color.resource) 
            svg_blob = svg_file.read().encode('utf-8')
            image.read(blob=svg_blob)
            png_image = image.make_blob("png32")

    with open(png_file, "wb") as out:
        out.write(png_image)


convert("dash.svg", "dash.png")