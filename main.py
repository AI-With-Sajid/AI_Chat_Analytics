# cd C:\Personal\AI_analytics\pythonProject\.venv\Scripts
# (base) PS C:\Personal\AI_analytics\pythonProject\.venv\Scripts> .\Activate.ps1
# (base) (.venv) PS C:\Personal\AI_analytics\pythonProject\.venv\Scripts> cd C:\Personal\AI_analytics\pythonProject
# (base) (.venv) PS C:\Personal\AI_analytics\pythonProject> streamlit run main.py

import re
import warnings
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from urlextract import URLExtract
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

extract = URLExtract()


def separate_users_and_messages(df):
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)
    return df

def preprocessor(data):
    pattern1 = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:am|pm)\s-\s"
    messages = re.split(pattern1, data)[1:]
    dates = re.findall(r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s(?:am|pm)', data)
    cleaned_dates = [date.replace('\u202f', '') for date in dates]
    df = pd.DataFrame({'user_message':messages, 'message_date': cleaned_dates})
    # new_messages = df['user_message'].tolist()
    # paragraph = '\n'.join(new_messages)
    paragraph = '\n'.join(df['user_message'].tolist()[:500])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df['message_date'] = pd.to_datetime(df['message_date']).dt.strftime('%Y-%m-%d %H:%M')
    df.rename(columns={'message_date':'date_time'}, inplace=True)
    df = separate_users_and_messages(df)
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['year'] = df['date_time'].dt.year
    df['month'] = df['date_time'].dt.month
    df['month_name'] = df['date_time'].dt.month_name()
    df['day'] = df['date_time'].dt.day
    df['hour'] = df['date_time'].dt.hour
    df['minute'] = df['date_time'].dt.minute
    return df, paragraph

def fetch_stats(selected_user,df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    # fetch the number of messages
    num_messages = df.shape[0]
    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)


def most_active_user(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})
    return x, df

def most_common_words(selected_user, df):
    f = open('C:\Personal\AI_analytics\pythonProject\stop_hinglish.txt', 'r')
    stop_words = f.read()
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != "<media omitted>"]
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    most_common_df = pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])


    words_to_remove = ['<media', 'omitted>']
    df_cleaned = most_common_df[~most_common_df['word'].isin(words_to_remove)]
    return df_cleaned.head(20)

def create_wordcloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user']==selected_user]

    wc = WordCloud(width = 500, height = 500, min_font_size = 10, background_color = 'white')
    df_wc = wc.generate(df['message'].str.cat(sep = " "))
    return df_wc

def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month', 'month_name']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(str(timeline['month_name'][i]) + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def sentiment_scores(sentence):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    # Convert scores to percentages
    sentiment_dict_percent = {
        'negative': sentiment_dict['neg'] * 100,
        'neutral': sentiment_dict['neu'] * 100,
        'positive': sentiment_dict['pos'] * 100,
    }
    return sentiment_dict_percent





st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #FFEA00;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("AI Chat Analytics")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df, paragraph = preprocessor(data)
    # st.dataframe(df)

    #fetching all the unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")
    selected_user = st.sidebar.selectbox('show analytics list', user_list)
    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages, words, num_media_messages, num_links = fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

    #sentiment analysis
    # st.title("Analyze Sentiment")
    # sentiment_dict = sentiment_scores(paragraph)
    # plt.bar(sentiment_dict.keys(), sentiment_dict.values(), color=['red', 'blue', 'green'])
    # plt.title('Sentiment Analysis')
    # plt.xlabel('Sentiment')
    # plt.ylabel('Percentage')
    # st.pyplot()

    st.title("Analyze Sentiment")
    sentiment_dict = sentiment_scores(paragraph)
    fig, ax = plt.subplots()
    ax.bar(sentiment_dict.keys(), sentiment_dict.values(), color=['red', 'blue', 'green'])
    ax.set_title('Sentiment Analysis')
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Percentage')
    st.pyplot(fig)

    #timeline
    st.title("Montly Timeline")
    timeline = monthly_timeline(selected_user, df)
    fig, ax = plt.subplots()
    ax.plot(timeline['time'], timeline['message'])
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    # # daily timeline
    # st.title("Daily Timeline")
    # daily_timeline = daily_timeline(selected_user, df)
    # fig, ax = plt.subplots()
    # ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
    # plt.xticks(rotation='vertical')
    # st.pyplot(fig)

    # finding the busiest users in the group(Group level)
    if selected_user == 'Overall':
        st.title('Most Busy Users')
        x, new_df = most_active_user(df)
        fig, ax = plt.subplots()

        col1, col2 = st.columns(2)

        with col1:
            ax.bar(x.index, x.values, color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.dataframe(new_df)


    st.title("Wordcloud")
    df_wc = create_wordcloud(selected_user, df)
    wordcloud_image = df_wc.to_image()
    st.image(wordcloud_image, caption='Word Cloud')

    st.title('Most Common Words')
    most_common_df = most_common_words(selected_user, df)
    col1, col2 = st.columns([1.5,3.5])
    with col1:
        st.dataframe(most_common_df)
    with col2:
        fig, ax = plt.subplots()
        ax.barh(most_common_df['word'], most_common_df['count'])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)