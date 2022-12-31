import os
from image_lib import *
from PIL import Image
from PIL import ImageFile
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report, f1_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
import joblib
import time

ImageFile.LOAD_TRUNCATED_IMAGES = True


class ScreenshotClassifier:
    def __init__(self, classifier, folder, target_size=target_size_best, resample_filter=Image.LANCZOS):
        self.classifier = classifier
        self.folder = folder
        self.target_size = target_size
        self.resample_filter = resample_filter
        self.model_path = os.path.join(folder, "model")
        self.data = {}
        self.latest_versionCode = 0

    def _load_train_data(self):
        print("Loading train data...")
        self.data["vectors"] = []
        self.data["labels"] = []
        for root, dirs, files in os.walk(self.folder):
            for file in files:
                if os.path.splitext(file)[1] not in ['.png', '.webp']:
                    continue
                versionCode = int(root.split('\\')[-1])
                if versionCode == 0:
                    continue
                if versionCode > self.latest_versionCode:
                    self.latest_versionCode = versionCode

                image = Image.open(os.path.join(root, file))
                image = resize_and_crop(image)
                image_array = np.array(image).ravel()
                self.data["vectors"].append(image_array)
                self.data["labels"].append(versionCode)

        # merge the old versions to one class
        for i, versionCode in enumerate(self.data["labels"]):
            self.data["labels"][i] = 0 if versionCode == self.latest_versionCode else 1

        print("Loading train data DONE!")
        print("Num: {}".format(len(self.data["vectors"])))
        print("-" * 40)

    def _load_predict_data(self):
        print("Loading predict data...")
        self.data["questions"] = []
        self.data["question_paths"] = []
        for root, dirs, files in os.walk(os.path.join(self.folder, "0")):
            for file in files:
                if os.path.splitext(file)[1] not in ['.png', '.webp']:
                    continue
                image = Image.open(os.path.join(root, file))
                image = resize_and_crop(image, self.target_size, self.resample_filter)
                image_array = np.array(image).ravel()
                self.data["questions"].append(image_array)
                self.data["question_paths"].append(os.path.join(root, file))
        print("Loading predict data DONE!")
        print("-" * 40)

    def k_fold_cross_validation(self, k=10, show_labels=False):
        if "vectors" not in self.data.keys():
            self._load_train_data()
        ground_truth = []
        predict = []

        time_start = time.time()
        kf = KFold(n_splits=k, shuffle=True, random_state=0)
        for i_fold, (train_index, test_index) in enumerate(kf.split(self.data["vectors"], self.data["labels"])):
            print("Start {}/{} fold... ".format(i_fold+1, k), end='')
            train_vectors = []
            train_labels = []
            for i in train_index:
                train_vectors.append(self.data["vectors"][i])
                train_labels.append(self.data["labels"][i])
            test_vectors = []
            test_labels = []
            for i in test_index:
                test_vectors.append(self.data["vectors"][i])
                test_labels.append(self.data["labels"][i])

            ground_truth += test_labels
            print("Training... ", end='')
            self.classifier.fit(train_vectors, train_labels)
            print("Predicting... ", end='')
            predict += self.classifier.predict(test_vectors).tolist()
            print("{}/{} fold DONE!".format(i_fold+1, k))
        time_end = time.time()

        if show_labels:
            print("Ground truth: ", ground_truth)
            print("Predict: ", predict)
        print("Time spent: {}s".format(int(time_end - time_start)))
        print(classification_report(ground_truth, predict, target_names=["brand new version", "old versions"]))
        return ground_truth, predict

    def predict_questions(self, load_model=True):
        self._load_predict_data()
        if load_model and os.path.exists(self.model_path):
            print("Loading model... ", end='')
            self.classifier = joblib.load(self.model_path)
        else:
            if "vectors" not in self.data.keys():
                self._load_train_data()
            print("Training... ", end='')
            self.classifier.fit(self.data["vectors"], self.data["labels"])
            joblib.dump(self.classifier, self.model_path)

        print("Predicting... (1: Outdated)")
        predict = self.classifier.predict(self.data['questions'])
        for i, path in enumerate(self.data['question_paths']):
            print('{}: {}'.format(path, predict[i]))


app_packages = {
    "FG": "com.boedec.hoel.frequencygenerator",
    "CPU-Z": "com.cpuid.cpu_z",
    "920": "com.jecelyin.editor.v2",
    "QR": "com.teacapps.barcodescanner",
    "Tri": "processing.test.trigonometrycircleandroid",
    "EC": "com.everycircuit.free",
    "2048": "com.androbaby.game2048",
    "BBTAN": "com.crater.bbtan",
}

def print_data_of_apps():
    print()

    for app_key in app_packages.keys():
        print('App: {}'.format(app_key))
        sc_classifier = ScreenshotClassifier(
            classifier=RandomForestClassifier(),
            folder=os.path.join(folder_screenshots, app_packages[app_key])
        )
        ground_truth, predict = sc_classifier.k_fold_cross_validation(k=10)

dict_classifiers = {
    '1NN': KNeighborsClassifier(n_neighbors=1),
    '3NN': KNeighborsClassifier(n_neighbors=3),
    '5NN': KNeighborsClassifier(n_neighbors=5),
    'RF': RandomForestClassifier(),
    'LR': LogisticRegression(),
    'SVC': SVC(),
    'DT': DecisionTreeClassifier(),
}

def print_data_of_classifiers():
    print()

    dict_f1_sum = {}
    for app_key in app_packages.keys():
        print('App: {}'.format(app_key))
        sc_classifier = ScreenshotClassifier(
            classifier=None,
            folder=os.path.join(folder_screenshots, app_packages[app_key])
        )
        for classifier_key in dict_classifiers.keys():
            print('Classifier: {}'.format(classifier_key))
            sc_classifier.classifier = dict_classifiers[classifier_key]
            ground_truth, predict = sc_classifier.k_fold_cross_validation(k=10)
            dict_f1_sum['{}+{}'.format(app_key, classifier_key)] = f1_score(ground_truth, predict)
    print(dict_f1_sum)


dict_resampling_filters = {
    'NEAREST': Image.NEAREST,
    'BOX': Image.BOX,
    'BILINEAR': Image.BILINEAR,
    'HAMMING': Image.HAMMING,
    'BICUBIC': Image.BICUBIC,
    'LANCZOS': Image.LANCZOS,
}


def print_data_of_resampling_filters():
    print()

    dict_f1_sum = {}
    for app_key in app_packages.keys():
        print('App: {}'.format(app_key))
        sc_classifier = ScreenshotClassifier(
            classifier=dict_classifiers['RF'],
            folder=os.path.join(folder_screenshots, app_packages[app_key])
        )
        for resampling_filter_key in dict_resampling_filters.keys():
            print('Resampling filter: {}'.format(resampling_filter_key))
            sc_classifier.resample_filter = dict_resampling_filters[resampling_filter_key]
            sc_classifier.data = {}
            ground_truth, predict = sc_classifier.k_fold_cross_validation(k=10)
            dict_f1_sum['{}+{}'.format(app_key, resampling_filter_key)] = f1_score(ground_truth, predict)
    print(dict_f1_sum)


dict_target_resolutions = {
    '9x16': (9, 16),
    '18x32': (18, 32),
    '36x64': (36, 64),
    '72x128': (72, 128),
    '135x240': (135, 240),
    '270x480': (270, 480),
    '540x960': (540, 960),
    '1080x1920': (1080, 1920),
}


def print_data_of_target_resolutions():
    print()

    dict_f1_sum = {}
    for app_key in app_packages.keys():
        print('App: {}'.format(app_key))
        sc_classifier = ScreenshotClassifier(
            classifier=dict_classifiers['RF'],
            folder=os.path.join(folder_screenshots, app_packages[app_key])
        )
        for target_resolution_key in dict_target_resolutions.keys():
            print('Target resolution: {}'.format(target_resolution_key))
            sc_classifier.target_size = dict_target_resolutions[target_resolution_key]
            sc_classifier.data = {}
            ground_truth, predict = sc_classifier.k_fold_cross_validation(k=10)
            dict_f1_sum['{}+{}'.format(app_key, target_resolution_key)] = f1_score(ground_truth, predict)
    print(dict_f1_sum)


def predict_app(package_name, load_model=True):
    sc_classifier = ScreenshotClassifier(
        classifier=dict_classifiers['RF'],
        folder=os.path.join(folder_screenshots, package_name)
    )
    sc_classifier.predict_questions(load_model=load_model)


if __name__ == '__main__':
    print_data_of_apps()
    # print_data_of_classifiers()
    # print_data_of_resampling_filters()
    # print_data_of_target_resolutions()

    # predict_app(package_name)
