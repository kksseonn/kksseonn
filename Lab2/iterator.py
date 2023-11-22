import csv
import os


class ImageIterator:
    def __init__(self, annotation_file, target_class):
        self.annotation_file = annotation_file
        self.target_class = target_class
        self.class_instances = self.load_annotation_file()
        self.index = 0
        self.prev_instances = set()

    def load_annotation_file(self):
        instances = []
        with open(self.annotation_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if len(row) == 3:
                    instance_class = os.path.split(
                        row[1])[-1].split("_")[0].split(".")[0]
                    if instance_class == self.target_class:
                        instances.append(row[1])
        return instances

    def __iter__(self):
        return self

    def __next__(self):
        while self.index < len(self.class_instances):
            instance = self.class_instances[self.index]
            self.index += 1
            if instance not in self.prev_instances:
                self.prev_instances.add(instance)
                return instance

        raise StopIteration("No more instances for the specified class.")


class ClassIterator:
    def __init__(self, csv_file: str, class_labels):
        self.csv_file = csv_file
        self.class_labels = class_labels
        self.image_iterators = {label: ImageIterator(
            csv_file, label) for label in class_labels}
        self.current_label_index = 0

    def next_image(self) -> str:
        """
        Get the next instance for the current class label.
        Returns:
        Optional[str]: The path to the next instance of the current class label, or None if instances are exhausted.
        """
        if not self.class_labels or self.current_label_index >= len(self.class_labels):
            return None

        current_class_label = self.class_labels[self.current_label_index]
        current_image_iterator = self.image_iterators[current_class_label]
        next_instance = next(current_image_iterator, None)

        if next_instance is not None:
            return next_instance
        else:
            self.current_label_index += 1
            return self.next_image()


if __name__ == "__main__":
    annotation_file = 'copy_dataset.csv'
    class_labels = ["tiger", "leopard"]
    iterator = ClassIterator(annotation_file, class_labels)

    instance = iterator.next_image()
    while instance is not None:
        print(instance)
        instance = iterator.next_image()
