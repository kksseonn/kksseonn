import pandas as pd
import json
from PIL import Image
import cv2


def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        channels = len(img.getbands())
    return height, width, channels


def get_pixel_count(image_path):
    img = cv2.imread(image_path)
    if img is not None:
        return img.size // img.itemsize
    else:
        print(f"Warning: Unable to read image at path {image_path}")
        return 0


def create_dataframe(csv_path):
    df = pd.read_csv(csv_path, header=None, names=[
                     'absolute_path', 'relative_path', 'class'], sep=',')
    df['label'] = df['class'].factorize()[0]

    class_mapping = {'leopard': 0, 'tiger': 1}
    df['numeric_label'] = df['class'].map(class_mapping)

    df['height'], df['width'], df['depth'] = zip(
        *df['absolute_path'].apply(get_image_dimensions))
    df['pixel_count'] = df['absolute_path'].apply(get_pixel_count)

    result_df = df[['class', 'absolute_path', 'numeric_label',
                    'height', 'width', 'depth', 'pixel_count']].copy()
    result_df.columns = ['class_name', 'absolute_path',
                         'numeric_label', 'height', 'width', 'depth', 'pixel_count']
    return result_df


def compute_statistics(df):
    image_dimensions_stats = df[['height', 'width',
                                 'depth', 'pixel_count']].describe()
    print("Statistics for image sizes and pixel count:")
    print(image_dimensions_stats)

    class_label_stats = df['numeric_label'].value_counts()
    print("\nStatistics for class labels:")
    print(class_label_stats)

    is_balanced = class_label_stats.min() == class_label_stats.max()
    print("\nThe data set is balanced:", is_balanced)


def filter_dataframe(input_df, target_label=None, max_height=None, max_width=None):
    filtered_df = input_df.copy()

    if target_label is not None:
        filtered_df = filtered_df[filtered_df['numeric_label'] == target_label]

    if max_height is not None:
        filtered_df = filtered_df[filtered_df['height'] <= max_height]

    if max_width is not None:
        filtered_df = filtered_df[filtered_df['width'] <= max_width]

    return filtered_df


def group_by_label_and_pixel_count(df):
    grouped_df = df.groupby('numeric_label')['pixel_count'].agg(
    ['min', 'max', 'mean']).reset_index()
    grouped_df.columns = ['numeric_label', 'min_pixel_count', 'max_pixel_count', 'mean_pixel_count']
    return grouped_df


if __name__ == "__main__":
    with open("Lab4/options.json", "r") as options_file:
        options = json.load(options_file)
    df = create_dataframe(options['annotation'])
    print(df)
    compute_statistics(df)

    target_label = options["target_label"]
    max_height = options["max_height"]
    max_width = options["max_width"]

    filtered_by_label_df = filter_dataframe(
        df, target_label=target_label, max_height=None, max_width=None)
    filtered_by_params_df = filter_dataframe(
        df, target_label=target_label, max_height=max_height, max_width=max_width)

    print(
        f"\nFiltered DataFrame for class label {target_label}:\n", filtered_by_label_df)
    print(
        f"\nFiltered DataFrame for class label {target_label}, height <= {max_height}, width <= {max_width}:\n", filtered_by_params_df)

    grouped_df = group_by_label_and_pixel_count(df)
    print("\nGrouped DataFrame by numeric label and pixel count:\n", grouped_df)
