# def fetch_stats(selected_user, df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#     num_messages = df.shape[0]
#     words = []
#     for message in df['message']:
#         words.extend(message.split())
#     return num_messages, len(words)
#
#     num_media_message = df[df['message'] == '<Media omitted>\n'].shape[0]
#
#     links = []
#     for message in df['message']:
#         links.extend(extract.find_urls(message))
#     return num_messages, len(words), num_media_message, len(links)


def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the numbersd[]]\\\# ages
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
