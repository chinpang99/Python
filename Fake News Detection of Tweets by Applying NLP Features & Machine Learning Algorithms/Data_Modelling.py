import pandas as pd
from imblearn.combine import SMOTETomek
from imblearn.under_sampling import NearMiss
from collections import Counter
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, confusion_matrix, plot_roc_curve, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 300)

enhanced_dataset = pd.DataFrame(pd.read_csv(r'enhanced_dataset.csv'))

# Linguistic Attributes
X = enhanced_dataset[['url_www', 'url_level', 'total_sentences', 'word_size', 'avg_word_per_sentence',
                      'no_of_words_in_title', 'count_punct', 'noun_density', 'verb_density', 'adjective_density',
                      'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density']]

# All Attributes (Tweets and Linguistic Attributes)
X = enhanced_dataset[['url_www', 'url_level', 'total_sentences', 'word_size', 'avg_word_per_sentence',
                      'no_of_words_in_title', 'count_punct', 'noun_density', 'verb_density', 'adjective_density',
                      'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density',
                      'total_retweets', 'total_favorites', 'percentage_avai_ids']]

Y = enhanced_dataset['target']

# Implementing Oversampling for Handling Imbalanced
smk = SMOTETomek(random_state=42)
X_res, y_res=smk.fit_sample(X, Y)

# Implementing Undersampling for Handling Imbalanced
nm = NearMiss()
X_res, y_res = nm.fit_sample(X, Y)

X_res.shape, y_res.shape
print('Original dataset shape {}'.format(Counter(Y)))
print('Resampled dataset shape {}'.format(Counter(y_res)), '\n')

# Visualization after perform SMOTE Sampling Technique
y_res.count()
ax = sns.countplot(y_res)
plt.title('Frequency of Fake News')
plt.xlabel('Target')
plt.ylabel('Frequency')

for p in ax.patches:
        ax.annotate('{:}'.format(p.get_height()), (p.get_x()+0.35, p.get_height()+50))

X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.40, random_state=100)

# ------ LOGISTIC REGRESSION (LR) Model-----
LR_model = LogisticRegression(solver='liblinear', random_state=100)
LR_model.fit(X_train, y_train)
print("The accuracy score for Logistic Regression (Train): ", LR_model.score(X_train, y_train)*100, '%')
print("Classification Report for Logistic Regression (Train): \n---------------------------------------\n",
      classification_report(y_train, LR_model.predict(X_train)))
print()
print("The accuracy score for Logistic Regression (Test): ", LR_model.score(X_test, y_test)*100, '%')
print("Classification Report for Logistic Regression (Test): \n---------------------------------------\n",
      classification_report(y_test, LR_model.predict(X_test)))
print("Precision for LR: ", 100 * precision_score(y_test, LR_model.predict(X_test)), '%')
print("Recall for LR: ", 100 * recall_score(y_test, LR_model.predict(X_test)), '%')
print("F1 for LR: ", 100 * f1_score(y_test, LR_model.predict(X_test)), '%')

# --- Confusion Matrix for Logistic Regression ---
lr_cm = confusion_matrix(y_test, LR_model.predict(X_test))
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(lr_cm)
ax.grid(False)
ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
ax.set_ylim(1.5, -0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, lr_cm[i, j], ha='center', va='center', color='red')

plt.show()

# --- Hyperparameter Tuning (Grid Search) Cross-Validation
param_grid = [
    {'penalty': ['l1', 'l2', 'elasticnet', 'none'],
     'C': np.logspace(-4, 4, 20),
     'solver': ['lbfgs', 'newton-cg', ' liblinear', 'sag', 'saga'],
     'max_iter': [100, 1000, 2500, 5000]
    }
]

clf = GridSearchCV(LR_model, param_grid=param_grid, cv=3, verbose=True, n_jobs=-1)
best_clf = clf.fit(X, Y)

# ------ SUPPORT VECTOR MACHINE (SVM) Model -----
SVM_model = SVC(random_state=100, kernel='linear')
SVM_model.fit(X_train, y_train)
print("The accuracy score for Support Vector Machine (Train): ", SVM_model.score(X_train, y_train)*100, '%')
print("Classification Report for Support Vector Machine (Train): \n---------------------------------------\n",
      classification_report(y_train, SVM_model.predict(X_train)))
print()
print("The accuracy score for Support Vector Machine (Test): ", SVM_model.score(X_test, y_test)*100, '%')
print("Classification Report for Support Vector Machine (Test): \n---------------------------------------\n",
      classification_report(y_test, SVM_model.predict(X_test)))
print("Precision for SVM: ", 100 * precision_score(y_test, SVM_model.predict(X_test)), '%')
print("Recall for SVM: ", 100 * recall_score(y_test, SVM_model.predict(X_test)), '%')
print("F1 for SVM: ", 100 * f1_score(y_test, SVM_model.predict(X_test)), '%')


# --- Confusion Matrix for Support Vector Machine ---
svm_cm = confusion_matrix(y_test, SVM_model.predict(X_test))
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(svm_cm)
ax.grid(False)
ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
ax.set_ylim(1.5, -0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, svm_cm[i, j], ha='center', va='center', color='red')

plt.show()


# -------- Hyperparameter Tuning GridSearchCV --------
# defining parameter range
param_grid = {'C': [0.1, 1, 10, 100, 1000],
              'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
              'kernel': ['rbf']}

svm_grid = GridSearchCV(SVM_model, param_grid, refit=True, verbose=3)

# fitting the model for grid search
svm_grid.fit(X_train, y_train)
print(svm_grid.best_params_)
print(svm_grid.best_estimator_)
print(svm_grid.best_score_)
svm_grid_predictions = svm_grid.predict(X_test)
print("The accuracy score for Support Vector Machine After Tuning: ", svm_grid.best_score_*100, '%')
print(classification_report(y_test, svm_grid_predictions))
print("Precision for SVM: ", 100 * precision_score(y_test, svm_grid_predictions), '%')
print("Recall for SVM: ", 100 * recall_score(y_test, svm_grid_predictions), '%')
print("F1 for SVM: ", 100 * f1_score(y_test, svm_grid_predictions), '%')


# ------ DECISION TREE (DT) CLASSIFIER -----
DT_Model = DecisionTreeClassifier(random_state=100,  min_samples_leaf=5)
DT_Model.fit(X_train, y_train)
print("The accuracy score for Decision Tree Classifier (Train): ", DT_Model.score(X_train, y_train)*100, '%')
print("Classification Report for Decision Tree Classifier (Train): \n---------------------------------------\n",
      classification_report(y_train, DT_Model.predict(X_train)))
print()
print("The accuracy score for Decision Tree Classifier (Test): ", DT_Model.score(X_test, y_test)*100, '%')
print("Classification Report for Decision Tree Classifier (Test): \n---------------------------------------\n",
      classification_report(y_test, DT_Model.predict(X_test)))
print("Precision for DT: ", 100 * precision_score(y_test, DT_Model.predict(X_test)), '%')
print("Recall for DT: ", 100 * recall_score(y_test, DT_Model.predict(X_test)), '%')
print("F1 for DT: ", 100 * f1_score(y_test, DT_Model.predict(X_test)), '%')

# --- Hyperparameter Tuning (Grid Search) Cross-Validation
param_dist = {
    "criterion": ["gini", "entropy"],
    "max_depth": [2, 4]
}

# perform hyperparameter tuning with 3-fold-cross-validation; n_jobs = use all the cores to perform this process
dt_grid = GridSearchCV(DT_Model, param_grid=param_dist, cv=3, n_jobs=-1)
dt_grid.fit(X_train, y_train)
print(dt_grid.best_params_)
print(dt_grid.best_estimator_)
print(dt_grid.best_score_)
dt_grid_predictions = dt_grid.predict(X_test)
print("The accuracy score for Decision Tree Classifier After Tuning: ", dt_grid.best_score_*100, '%')
print(classification_report(y_test, dt_grid_predictions))
print("Precision for DT: ", 100 * precision_score(y_test, dt_grid_predictions), '%')
print("Recall for DT: ", 100 * recall_score(y_test, dt_grid_predictions), '%')
print("F1 for DT: ", 100 * f1_score(y_test, dt_grid_predictions), '%')


# --- Confusion Matrix for Decision Tree Classifier ---
dt_cm = confusion_matrix(y_test, DT_Model.predict(X_test))
# dt_cm = confusion_matrix(y_test, dt_grid.predict(X_test))
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(dt_cm)
ax.grid(False)
ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
ax.set_ylim(1.5, -0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, dt_cm[i, j], ha='center', va='center', color='red')

plt.show()


# ------ RANDOM FOREST CLASSIFIER -----
RF_Model = RandomForestClassifier(random_state=100)
RF_Model.fit(X_train, y_train)
print("The accuracy score for Random Forest Classifier (Train): ", RF_Model.score(X_train, y_train)*100, '%')
print("Classification Report for Random Forest Classifier (Train): \n---------------------------------------\n",
      classification_report(y_train, RF_Model.predict(X_train)))
print()
print("The accuracy score for Random Forest Classifier (Test): ", RF_Model.score(X_test, y_test)*100, '%')
print("Classification Report for Random Forest Classifier (Test): \n---------------------------------------\n",
      classification_report(y_test, RF_Model.predict(X_test)))
print("Precision for RF: ", 100 * precision_score(y_test, RF_Model.predict(X_test)), '%')
print("Recall for RF: ", 100 * recall_score(y_test, RF_Model.predict(X_test)), '%')
print("F1 for RF: ", 100 * f1_score(y_test, RF_Model.predict(X_test)), '%')

# --- StratifiedKFold Cross-Validation --------------
cross_val_score(RF_Model, X, Y, cv=5, scoring='accuracy').mean()

# ---- Identify Variable Importance ---------
importance = RF_Model.feature_importances_
for name, importance in zip(X, importance):
    print(name, "=", importance)


# AUC Curve
dt_disp = plot_roc_curve(RF_Model, X_test, y_test)
plt.show()

# --- Hyperparameter Tuning (Grid Search) Cross-Validation ---
n_estimators = [int(x) for x in np.linspace(start=10, stop=80, num=10)]
max_features = ['auto','sqrt']
max_depth = [2,4]
min_samples_split = [2,5]
min_samples_leaf = [1,2]
bootstrap = [True,False]

# defining parameter range
param_grid = {
    'n_estimators': n_estimators,
    'max_features': max_features,
    'max_depth': max_depth,
    'min_samples_split': min_samples_split,
    'min_samples_leaf': min_samples_leaf,
    'bootstrap': bootstrap
}

rf_grid = GridSearchCV(estimator=RF_Model, param_grid=param_grid, cv=3, verbose=2, n_jobs=4)
# fitting the model for grid search
rf_grid.fit(X_train, y_train)
# print best parameter after tuning
print(rf_grid.best_params_)
# print how our model looks after hyper-parameter tuning
print(rf_grid.best_estimator_)
print(rf_grid.best_score_)
grid_predictions = rf_grid.predict(X_test)
# print classification report
print("The accuracy score for Random Forest Classifier After Tuning: ", rf_grid.score(X_test, y_test)*100, '%')
print(classification_report(y_test, grid_predictions))
print("Precision for RF: ", 100 * precision_score(y_test, grid_predictions), '%')
print("Recall for RF: ", 100 * recall_score(y_test, grid_predictions), '%')
print("F1 for RF: ", 100 * f1_score(y_test, grid_predictions), '%')


# --- Confusion Matrix for Random Forest Classifier ---
rf_cm = confusion_matrix(y_test, RF_Model.predict(X_test))
# rf_cm = confusion_matrix(y_test, rf_grid.predict(X_test))
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(rf_cm)
ax.grid(False)
ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
ax.set_ylim(1.5, -0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, rf_cm[i, j], ha='center', va='center', color='red')

plt.show()


# ------ NAIVE BAYES Classifier-----
# Create a Gaussian Classifier
gnb = GaussianNB()
# Train the model using the training sets
gnb.fit(X_train, y_train)
print("The accuracy score for Naive Bayes (Train): ", gnb.score(X_train, y_train)*100, '%')
print("Classification Report for Naive Bayes (Train): \n---------------------------------------\n",
      classification_report(y_train, gnb.predict(X_train)))
print()
print("The accuracy score for Naive Bayes (Test): ", gnb.score(X_test, y_test)*100, '%')
print("Classification Report for Naive Bayes (Test): \n---------------------------------------\n",
      classification_report(y_test, gnb.predict(X_test)))
print("Precision for GNB: ", 100 * precision_score(y_test, gnb.predict(X_test)), '%')
print("Recall for GNB: ", 100 * recall_score(y_test, gnb.predict(X_test)), '%')
print("F1 for GNB: ", 100 * f1_score(y_test, gnb.predict(X_test)), '%')


# --- Confusion Matrix for Naive Bayes ---
gnb_cm = confusion_matrix(y_test, gnb.predict(X_test))
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(gnb_cm)
ax.grid(False)
ax.xaxis.set(ticks=(0, 1), ticklabels=('Predicted 0s', 'Predicted 1s'))
ax.yaxis.set(ticks=(0, 1), ticklabels=('Actual 0s', 'Actual 1s'))
ax.set_ylim(1.5, -0.5)
for i in range(2):
    for j in range(2):
        ax.text(j, i, gnb_cm[i, j], ha='center', va='center', color='red')

plt.show()



