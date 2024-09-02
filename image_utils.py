from PIL import Image
import io


def resize_image_to_kb(input_image_path, output_image_path, target_size_kb):
    """
    Resize an image to a target size in KB.
    将图像调整大小至目标文件大小（KB）。

    :param input_image_path: Path to the input image. 输入图像的路径。
    :param output_image_path: Path to save the resized image. 保存调整大小后的图像的路径。
    :param target_size_kb: Target size in KB. 目标文件大小（KB）。
    
    Example: 
    resize_image_to_kb('input_image.jpg', 'output_image.jpg', 50)
    """
    
    # Open an image file
    with Image.open(input_image_path) as img:
        # Convert image to RGB mode if it's not
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Initial quality value
        quality = 95
        
        while True:
            # Create a BytesIO object to hold the image data in memory
            img_byte_arr = io.BytesIO()
            
            # Save the image to the BytesIO object with the current quality
            img.save(img_byte_arr, format='JPEG', quality=quality)
            
            # Get the size of the image in KB
            img_size_kb = len(img_byte_arr.getvalue()) / 1024
            
            # Check if the image size is within the target size
            if img_size_kb <= target_size_kb:
                # If the image is smaller than the target size, add padding
                if img_size_kb < target_size_kb:
                    padding_size = int((target_size_kb * 1024) - len(img_byte_arr.getvalue()))
                    padding = b'\x00' * padding_size
                    img_byte_arr.write(padding)
                
                # Save the image to the output path
                with open(output_image_path, 'wb') as f:
                    f.write(img_byte_arr.getvalue())
                break
            
            # Reduce the quality if the image is still too large
            quality -= 5
            
            # Ensure quality does not go below 1
            if quality < 1:
                quality = 1
