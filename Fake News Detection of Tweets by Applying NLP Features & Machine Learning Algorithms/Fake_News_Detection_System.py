from flask import Flask, request, render_template
import pickle
from imblearn.combine import SMOTETomek
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import nltk
import pandas as pd
# download punkt package
nltk.download('punkt')

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def predict():
    global url
    url = request.form.get('url')
    str1 = url
    if url.startswith('http') or url.startswith('https'):
        str1 = url
    else:
        str1 = 'http://' + url

    print(str1)
    dataset = pd.DataFrame(pd.read_csv(r'enhanced_dataset.csv'))
    a = pd.DataFrame(pd.read_csv(r'news_content.csv'))
    a = a.dropna()
    X = dataset[['url_www', 'url_level', 'total_sentences', 'word_size', 'avg_word_per_sentence',
                 'no_of_words_in_title', 'count_punct', 'noun_density', 'verb_density', 'adjective_density',
                 'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density',
                 'total_retweets', 'total_favorites', 'percentage_avai_ids']]
    Y = dataset['target']
    smk = SMOTETomek(random_state=42)
    X_res, y_res = smk.fit_sample(X, Y)
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.20, random_state=100)
    RF_Model= RandomForestClassifier(random_state=100)
    RF_Model.fit(X_train, y_train)
    print("The accuracy score for Random Forest Classifier (Test): ", RF_Model.score(X_test, y_test) * 100, '%')
    print("Classification Report for Random Forest Classifier (Test): \n---------------------------------------\n",
          classification_report(y_test, RF_Model.predict(X_test)))
    filename = 'FinalModel.sav'
    pickle.dump(RF_Model, open(filename, 'wb'))
    load_model = pickle.load(open('FinalModel.sav', 'rb'))
    result = load_model.score(X_test, y_test)
    print('The accuracy of the classification: ', result)
    unseen_data = pd.read_csv(r'unseen_data.csv')
    b = unseen_data[unseen_data['news_url'].str.contains(url)]
    d = a[a['news_url'].str.contains(url)]
    c = b[['url_www', 'url_level', 'total_sentences', 'word_size', 'avg_word_per_sentence',
           'no_of_words_in_title', 'count_punct', 'noun_density', 'verb_density', 'adjective_density',
           'adverb_density', 'preposition_density', 'conjunction_density', 'interjection_density',
           'total_retweets', 'total_favorites','percentage_avai_ids']]
    news_title = d['title'].values
    news_content = d['news_content'].values
    pred = RF_Model.predict(c)
    a = 'hi'
    b = 'bye'
    if pred == 0:
        a = '"REAL"'
        b = 'color:#00e600'
        c = 'https://media.giphy.com/media/l378blSjkootPNzTq/giphy.gif'
    elif pred == 1:
        a = '"Fake"'
        b = 'color:red'
        c = 'https://media.giphy.com/media/26n6xXh5UiF0BZx7y/giphy.gif'
    else:
        a = 'Unable to Predict'
    return render_template('index.html', gif=c, color=b, predicted_result='{} News'.format(a), news_title='News Title: {}'.format(news_title),
                           news_content='News Content: {}'.format(news_content), news_url=str1, str2='Link to the News Content')


if __name__=="__main__":
    app.run(debug=True)