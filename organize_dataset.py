import os
import shutil
from pathlib import Path
import random

# Configuration
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
IMAGES_DIR = BASE_DIR / "datasets" / "images"
LABELS_DIR = BASE_DIR / "datasets" / "labels"

# Class mapping
CLASS_MAPPING = {
    # Dataset 1 (banana_data)
    'unripe': 0,        # Mentah
    'ripe': 1,          # Matang
    'overripe': 2,      # Busuk
    'rotten': 2,        # Busuk
    
    # Dataset 2 (Banana ripeness)
    'Mentah': 0,
    'Setengah-mentah': 0,
    'Matang': 1,
    'Terlalu-matang': 2,
}

# Split ratio
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1

def create_folders():
    """Create necessary folders"""
    for split in ['train', 'val', 'test']:
        (IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
        (LABELS_DIR / split).mkdir(parents=True, exist_ok=True)
    print("✅ Folders created successfully!")

def get_all_images():
    """Collect all images from raw datasets"""
    all_images = []
    
    # Supported image extensions
    image_exts = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    # Scan all folders in raw directory
    for dataset_folder in RAW_DIR.iterdir():
        if not dataset_folder.is_dir():
            continue
            
        print(f"📂 Scanning: {dataset_folder.name}")
        
        # Look for images in all subdirectories
        for root, dirs, files in os.walk(dataset_folder):
            folder_name = Path(root).name
            
            # Check if folder name matches a class
            if folder_name in CLASS_MAPPING:
                class_id = CLASS_MAPPING[folder_name]
                
                for file in files:
                    if Path(file).suffix in image_exts:
                        all_images.append({
                            'path': Path(root) / file,
                            'class_id': class_id,
                            'class_name': folder_name
                        })
    
    print(f"✅ Found {len(all_images)} images total")
    return all_images

def create_yolo_label(image_info):
    """Create YOLO format label (dummy bounding box covering full image)"""
    # For now, create a label that covers the whole image
    # Later you can use actual bounding boxes if available
    class_id = image_info['class_id']
    # Format: class_id x_center y_center width height (normalized 0-1)
    return f"{class_id} 0.5 0.5 0.8 0.8\n"

def split_and_copy_dataset(all_images):
    """Split dataset into train/val/test and copy files"""
    
    # Shuffle images
    random.shuffle(all_images)
    
    total = len(all_images)
    train_size = int(total * TRAIN_RATIO)
    val_size = int(total * VAL_RATIO)
    
    splits = {
        'train': all_images[:train_size],
        'val': all_images[train_size:train_size + val_size],
        'test': all_images[train_size + val_size:]
    }
    
    # Copy images and create labels
    for split_name, images in splits.items():
        print(f"\n📋 Processing {split_name} split ({len(images)} images)...")
        
        for idx, img_info in enumerate(images, 1):
            src_path = img_info['path']
            
            # New filename: class_split_index.ext
            new_name = f"{img_info['class_name']}_{split_name}_{idx:04d}{src_path.suffix}"
            
            # Copy image
            dst_image = IMAGES_DIR / split_name / new_name
            shutil.copy2(src_path, dst_image)
            
            # Create label file
            label_name = dst_image.stem + '.txt'
            dst_label = LABELS_DIR / split_name / label_name
            
            with open(dst_label, 'w') as f:
                f.write(create_yolo_label(img_info))
            
            if idx % 50 == 0:
                print(f"  ✓ Processed {idx}/{len(images)} images...")
        
        print(f"✅ {split_name} split complete!")
    
    return splits

def print_summary(splits):
    """Print dataset summary"""
    print("\n" + "="*60)
    print("📊 DATASET SUMMARY")
    print("="*60)
    
    class_names = ['Mentah', 'Matang', 'Busuk']
    
    for split_name, images in splits.items():
        print(f"\n{split_name.upper()}:")
        print(f"  Total: {len(images)} images")
        
        # Count by class
        class_counts = {0: 0, 1: 0, 2: 0}
        for img in images:
            class_counts[img['class_id']] += 1
        
        for class_id, count in class_counts.items():
            print(f"  - {class_names[class_id]}: {count} images")
    
    print("\n" + "="*60)

def create_dataset_yaml():
    """Create dataset.yaml configuration file"""
    yaml_content = """# Banana Detection Dataset Configuration
# Path relative to YOLOv5 directory

path: ../datasets
train: images/train
val: images/val
test: images/test

# Number of classes
nc: 3

# Class names
names: ['Mentah', 'Matang', 'Busuk']
"""
    
    yaml_path = BASE_DIR / "datasets" / "dataset.yaml"
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"✅ Created dataset.yaml at {yaml_path}")

def main():
    print("🍌 BANANA DATASET ORGANIZER")
    print("="*60)
    
    # Step 1: Create folder structure
    print("\n1️⃣ Creating folder structure...")
    create_folders()
    
    # Step 2: Collect all images
    print("\n2️⃣ Collecting images from raw datasets...")
    all_images = get_all_images()
    
    if len(all_images) == 0:
        print("❌ No images found! Check your raw dataset folders.")
        return
    
    # Step 3: Split and copy dataset
    print("\n3️⃣ Splitting and organizing dataset...")
    splits = split_and_copy_dataset(all_images)
    
    # Step 4: Create dataset.yaml
    print("\n4️⃣ Creating dataset configuration...")
    create_dataset_yaml()
    
    # Step 5: Print summary
    print_summary(splits)
    
    print("\n✅ DATASET ORGANIZATION COMPLETE!")
    print(f"📁 Images: {IMAGES_DIR}")
    print(f"📁 Labels: {LABELS_DIR}")
    print(f"📄 Config: {BASE_DIR / 'datasets' / 'dataset.yaml'}")

if __name__ == "__main__":
    main()