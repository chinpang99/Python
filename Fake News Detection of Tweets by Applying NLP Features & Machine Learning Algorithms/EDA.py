import pandas as pd
from sklearn.impute import KNNImputer
import numpy as np
import matplotlib.pyplot as plt
import wordcloud
import seaborn as sns
from imblearn.combine import SMOTETomek


enhanced_dataset = pd.read_csv(r'enhanced_dataset.csv')
news_content = pd.read_csv(r'news_content.csv')
enhanced_dataset_before_transformation = pd.read_csv(r'enhanced_dataset_before_transformation.csv')

# Sanity Check
print("Top 5 Rows of Enhanced FakeNewsNet Dataset:\n", enhanced_dataset.head())
print()

print("Total Number of Rows:\n", enhanced_dataset.count())
print()

# Checking for null values
print("Total Number of Null:\n", enhanced_dataset.isnull().sum())

# Checking for duplicated rows
print("Total Number of Duplicated Rows:\n", enhanced_dataset.duplicated().sum())
print()

print("Summary Statistics:\n", enhanced_dataset.describe())

# Print the skewness of the enhanced FakeNewsNet dataset
print(enhanced_dataset.skew())

# ------------------- DATA CLEANING ----------------------------

# ---- IMPUTING MISSING VALUE -------
# initialize iterative imputer and fitting it with columns to be imputed
KNNimputer = KNNImputer(n_neighbors=2)

# fitting the data and imputing the missing values
enhanced_dataset[['total_retweets', 'total_favorites', 'total_ids', 'total_available_ids', 'percentage_avai_ids']] = \
    KNNimputer.fit_transform(enhanced_dataset[['total_retweets', 'total_favorites', 'total_ids', 'total_available_ids',
                                               'percentage_avai_ids']])


# ---- DATA TRANSFORMATION: LOG TRANSFORMATION -------
data_transformation = ['avg_word_per_sentence', 'total_sentences', 'word_size', 'count_punct',
                       'interjection_density', 'total_retweets', 'total_favorites']

enhanced_dataset[data_transformation] = enhanced_dataset[data_transformation].apply(lambda x: np.log(x+1))

# Final Enhanced Dataset written in CSV format
enhanced_dataset.to_csv("enhanced_dataset.csv", index=False)


# ---------------------------- DATA VISUALIZATION ---------------------------------

# ----------------- BAR CHART -----------------
# Bar Chart for Researcher Target Variable
researcher_dataset = pd.DataFrame(pd.read_csv(r'researcher_dataset.csv'))
researcher_dataset.groupby(['target'])['target'].count()
ax = sns.countplot(researcher_dataset['target'])
plt.title('Frequency of Fake News')
plt.xlabel('Target')
plt.ylabel('Frequency')

for p in ax.patches:
        ax.annotate('{:}'.format(p.get_height()), (p.get_x()+0.35, p.get_height()+50))



# Bar Chart for Fake and Real News Data
X = enhanced_dataset[['url_www', 'url_level', 'total_sentences', 'word_size', 'avg_word_per_sentence',
                      'no_of_words_in_title', 'count_punct', 'noun_density', 'verb_density', 'adjective_density',
                      'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density',
                      'total_retweets', 'total_favorites', 'percentage_avai_ids']]

Y = enhanced_dataset['target']

# Implementing Oversampling for Handling Imbalanced
smk = SMOTETomek(random_state=42)
X_res, y_res=smk.fit_sample(X, Y)

fig, ax = plt.subplots()
after_sampling = pd.DataFrame(data=y_res, columns=['target'])
after_sampling['sampling'] = 1
before_sampling = pd.DataFrame(data=enhanced_dataset['target'], columns=['target'])
before_sampling['sampling'] = 0
merge_dataset = pd.concat([after_sampling,before_sampling])

real_news = merge_dataset[merge_dataset['target'] == 0]
real_newss = real_news['sampling']
fake_news = merge_dataset[merge_dataset['target'] == 1]
fake_newss = fake_news['sampling']
plt.hist((fake_newss, real_newss), 2, label=("Before Oversampling", "After Oversampling"))
plt.title('Comparison Between Before and After Oversampling', fontsize=30)
plt.legend(fontsize=14)
plt.xticks((0.25, 0.75), ('Fake News', 'Real News'), fontsize=25)
for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    label.set_fontsize(16)

# ----------------- WORD CLOUD -----------------

fakenews_wordcloud = news_content[news_content['target'].eq(1)]['title']
realnews_wordcloud = news_content[news_content['target'].eq(0)]['title']

# ----------------- REAL NEWS WORD CLOUD -----------------
real_news_word_cloud = wordcloud.WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(' '.join(realnews_wordcloud))
plt.figure(figsize=[20, 10])
plt.imshow(real_news_word_cloud)
plt.axis("off")
plt.title('WORDCLOUD FOR REAL NEWS TITLE', fontsize=30)
plt.show()

# ----------------- FAKE NEWS WORD CLOUD -----------------
fake_news_word_cloud = wordcloud.WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(' '.join(fakenews_wordcloud))
plt.figure(figsize=[20, 10])
plt.imshow(fake_news_word_cloud)
plt.axis("off")
plt.title('WORDCLOUD FOR FAKE NEWS TITLE', fontsize=30)
plt.show()


# ----------------- KDE PLOT -----------------
researcher_dataset = pd.read_csv(r'researcher_dataset.csv')
no_of_words_in_title_real_news = researcher_dataset['no_of_words_in_title'][researcher_dataset['target'] == 0]
no_of_words_in_title_fake_news = researcher_dataset['no_of_words_in_title'][researcher_dataset['target'] == 1]
fig, ax = plt.subplots()
fig.suptitle('Total Number of Words in Title', fontsize=30)
ax.set_xlabel('Average Number of Words', fontsize=25)
ax.set_ylabel('Density', fontsize=25)
sns.kdeplot(no_of_words_in_title_real_news, ax=ax, shade=True)
sns.kdeplot(no_of_words_in_title_fake_news, ax=ax, shade=True)
for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    label.set_fontsize(16)
