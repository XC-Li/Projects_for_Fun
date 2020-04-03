"""
Utility functions
Such as data loading, augmentation, and evaluation
By: Xiaochi(George)Li
"""
from typing import List, Dict, Tuple
import cv2 as cv
import numpy as np
import pandas as pd
from tqdm import tqdm


def load_single_image(image_file: str, resize_shape: Tuple[int, int]) -> np.ndarray:
    """Load single image to numpy array"""
    f = open(image_file, "rb")
    chunk = f.read()
    chunk_arr = np.frombuffer(chunk, dtype=np.uint8)
    image = cv.imdecode(chunk_arr, cv.IMREAD_UNCHANGED)
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = cv.resize(image, (resize_shape[1], resize_shape[0]))
    return image


def load_data_with_augmentation(label_csv: str = 'GraphisLabel.csv', image_row: int = 200, image_col: int = 300, test_size: float = 0.3):
    label_df = pd.read_csv(label_csv, encoding='gbk', names=['link', 'file_location', 'label'])
    np.random.seed(42)
    test_select = np.random.choice(len(label_df), round(len(label_df) * test_size), replace=False)  # no replacement sampling
    train_df = label_df.loc[~label_df.index.isin(test_select)]
    test_df = label_df.loc[label_df.index.isin(test_select)]  # test data, keep original
    normal_count = sum(train_df.label == '-')
    oppai_count = sum(train_df.label == '+')
    print(normal_count, oppai_count)
    total_count = normal_count + oppai_count * 14
    print(total_count)
    image_data = np.zeros((total_count, image_row, image_col, 3))
    augmented_label = np.zeros(total_count)
    new_index = 0
    normal_number = oppai_number = 0
    for index, row in tqdm(train_df.iterrows(), total=len(train_df)):
        # print(row.label, new_index)
        original_image = load_single_image(row.file_location, (image_row, image_col))
        if row.label == '-':  # non-oppai image, only load without augmentation
            image_data[new_index] = original_image
            augmented_label[new_index] = 0
            normal_number += 1
            new_index += 1
        else:  # oppai image, load and augmentation (w/flip and rotate -45 ~ 45)
            for (i, r) in [(0, 0), (1, 15), (2, 30), (3, 45), (4, -15), (5, -30), (6, -45)]:
                image_data[new_index + i] = rotate(original_image, r)
                augmented_label[new_index + i] = 1
            flipped_image = flip_left_right(original_image)
            for (i, r) in [(7, 0), (8, 15), (9, 30), (10, 45), (11, -15), (12, -30), (13, -45)]:
                image_data[new_index + i] = rotate(flipped_image, r)
                augmented_label[new_index + i] = 1
            oppai_number += 1
            new_index += 14
    print(image_data.shape, augmented_label.shape)
    return image_data, augmented_label


def flip_left_right(image: np.ndarray) -> np.ndarray:
    return np.fliplr(image)


def rotate(image: np.ndarray, rotate_degree: int) -> np.ndarray:
    rows = image.shape[0]
    cols = image.shape[1]
    center_x = cols // 2
    center_y = rows // 2
    rotation_matrix = cv.getRotationMatrix2D((center_x, center_y), rotate_degree, 1)  # rotation center
    image = cv.warpAffine(image, rotation_matrix, (cols, rows))
    assert image.shape == (rows, cols, 3)
    return image


def change_brightness():
    pass


if __name__ == '__main__':
    load_data_with_augmentation()
