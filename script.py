import gradio as gr
from deep_translator import GoogleTranslator
from modules.utils import gradio
from modules import chat, ui_chat

params = {
    "user_input_activate": True,
    "model_output_activate": True,
    "user_language": "zh-TW",
    "model_language": 'en',
    'show_model_original_output': False
}

user_name = '{{_|_|}}'
bot_name = '{{_|}}'

language_codes = {
    'Afrikaans': 'af',
    'Albanian': 'sq',
    'Amharic': 'am',
    'Arabic': 'ar',
    'Armenian': 'hy',
    'Azerbaijani': 'az',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bengali': 'bn',
    'Bosnian': 'bs',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Cebuano': 'ceb',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Corsican': 'co',
    'Croatian': 'hr',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'English': 'en',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Finnish': 'fi',
    'French': 'fr',
    'Frisian': 'fy',
    'Galician': 'gl',
    'Georgian': 'ka',
    'German': 'de',
    'Greek': 'el',
    'Gujarati': 'gu',
    'Haitian Creole': 'ht',
    'Hausa': 'ha',
    'Hawaiian': 'haw',
    'Hebrew': 'iw',
    'Hindi': 'hi',
    'Hmong': 'hmn',
    'Hungarian': 'hu',
    'Icelandic': 'is',
    'Igbo': 'ig',
    'Indonesian': 'id',
    'Irish': 'ga',
    'Italian': 'it',
    'Japanese': 'ja',
    'Javanese': 'jw',
    'Kannada': 'kn',
    'Kazakh': 'kk',
    'Khmer': 'km',
    'Korean': 'ko',
    'Kurdish': 'ku',
    'Kyrgyz': 'ky',
    'Lao': 'lo',
    'Latin': 'la',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Luxembourgish': 'lb',
    'Macedonian': 'mk',
    'Malagasy': 'mg',
    'Malay': 'ms',
    'Malayalam': 'ml',
    'Maltese': 'mt',
    'Maori': 'mi',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Myanmar (Burmese)': 'my',
    'Nepali': 'ne',
    'Norwegian': 'no',
    'Nyanja (Chichewa)': 'ny',
    'Pashto': 'ps',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese (Portugal, Brazil)': 'pt',
    'Punjabi': 'pa',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Samoan': 'sm',
    'Scots Gaelic': 'gd',
    'Serbian': 'sr',
    'Sesotho': 'st',
    'Shona': 'sn',
    'Sindhi': 'sd',
    'Sinhala (Sinhalese)': 'si',
    'Slovak': 'sk',
    'Slovenian': 'sl',
    'Somali': 'so',
    'Spanish': 'es',
    'Sundanese': 'su',
    'Swahili': 'sw',
    'Swedish': 'sv',
    'Tagalog (Filipino)': 'tl',
    'Tajik': 'tg',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Ukrainian': 'uk',
    'Urdu': 'ur',
    'Uzbek': 'uz',
    'Vietnamese': 'vi',
    'Welsh': 'cy',
    'Xhosa': 'xh',
    'Yiddish': 'yi',
    'Yoruba': 'yo',
    'Zulu': 'zu'
}

user_to_model = GoogleTranslator(source=params['user_language'], target=params['model_language'])
model_to_user = GoogleTranslator(source=params['model_language'], target=params['user_language'])

def toggle_text_in_history(history):
    for i, entry in enumerate(history['visible']):
        if params['show_model_original_output']:
            reply:str = history['internal'][i][1]
            history['visible'][i][1] = "{}</original_str>\n\n> {}".format(history['visible'][i][1].split('</original_str>')[0], reply.replace('\n', '\n> ' * 2))
        else:
            history['visible'][i][1] = "{}".format(history['visible'][i][1].split('</original_str>')[0])

    return history

def input_modifier(string: str, state):
    """
    This function is applied to your text inputs before
    they are fed into the model.
    """
    if not params['user_input_activate']:
        return string

    string = string.replace(state['name2'], bot_name).replace(state['name1'], user_name)

    tmp_str = string
    code_index_list = []
    code_index_map = {}
    i = 0
    j = tmp_str.find('```')
    while tmp_str.find('```', j) != -1:
        if i % 2 == 0:
            code_index_list.append([])
        j = tmp_str.find('```', code_index_list[-1][-1] + 3 if len(code_index_list[-1]) > 0 else 0)
        code_index_list[-1].append(j)
        i += 1
        j += 3

    if len(code_index_list) > 0:
        if len(code_index_list[-1]) == 1:
            code_index_list = code_index_list[:-1]
        tmp_str = ''
        for i, code_index in enumerate(code_index_list):
            code_index_map[i + 1] = string[code_index[0]: code_index[1] + 3]
        for i, code_index in enumerate(code_index_list):
            tmp_str += string[:code_index[0]] + f'{{{{{"_" * (i + 1)}}}}}' + string[code_index[1] + 3:]
        string = tmp_str

    string = user_to_model.translate(string).replace(bot_name, state['name2']).replace(user_name, state['name1'])

    if len(code_index_list) > 0:
        for k, v in code_index_map.items():
            string = string.replace(f'{{{{{"_" * (k + 1)}}}}}', v)

    return string

def output_modifier(string: str, state):
    """
    This function is applied to the model outputs.
    """
    if not params['model_output_activate']:
        return string

    original_str = string

    audio_index = string.find('</audio>')
    audio_str = ''
    if audio_index != -1 and string.startswith('<audio>'):
        audio_str = string[: audio_index + len('</audio>')]
        string = string[audio_index + len('</audio>'):]

    string = string.replace(state['name2'], bot_name).replace(state['name1'], user_name)

    tmp_str = string
    code_index_list = []
    code_index_map = {}
    i = 0
    j = tmp_str.find('```')
    while tmp_str.find('```', j) != -1:
        if i % 2 == 0:
            code_index_list.append([])
        j = tmp_str.find('```', code_index_list[-1][-1] + 3 if len(code_index_list[-1]) > 0 else 0)
        code_index_list[-1].append(j)
        i += 1
        j += 3

    if len(code_index_list) > 0:
        if len(code_index_list[-1]) == 1:
            code_index_list = code_index_list[:-1]
        tmp_str = ''
        for i, code_index in enumerate(code_index_list):
            code_index_map[i+1] = string[code_index[0]: code_index[1]+3]
        for i, code_index in enumerate(code_index_list):
            tmp_str += string[:code_index[0]] + f'{{{{{"_" * (i + 1)}}}}}' + string[code_index[1]+3:]
        string = tmp_str

    string = audio_str + model_to_user.translate(string).replace(bot_name, state['name2']).replace(user_name, state['name1'])
    if params['show_model_original_output']:
        string += '</original_str>\n\n> ' + original_str.replace('\n', '\n> ' * 2)

    if len(code_index_list) > 0:
        for k, v in code_index_map.items():
            string = string.replace(f'{{{{{"_" * k}}}}}', v)

    return string


def bot_prefix_modifier(string):
    """
    This function is only applied in chat mode. It modifies
    the prefix text for the Bot and can be used to bias its
    behavior.
    """

    return string


def ui():
    # Finding the user_language name from the user_language code to use as the default value
    user_language_name = list(language_codes.keys())[list(language_codes.values()).index(params['user_language'])]
    model_language_name = list(language_codes.keys())[list(language_codes.values()).index(params['model_language'])]

    # Gradio elements
    with gr.Accordion("Google translate", open=True):
        with gr.Row():
            user_activate = gr.Checkbox(value=params['user_input_activate'], label='Activate user\'s input translation')
            model_activate = gr.Checkbox(value=params['model_output_activate'], label='Activate model\'s output translation')
            show_model_original_output = gr.Checkbox(value=params['show_model_original_output'], label='Show model\'s original output')

        with gr.Row():
            user_language = gr.Dropdown(value=user_language_name, choices=[k for k in language_codes], label='User Language')
            model_language = gr.Dropdown(value=model_language_name, choices=[k for k in language_codes], label='Model Language')

    # Event functions to update the parameters in the backend
    user_activate.change(lambda x: params.update({"user_input_activate": x}), user_activate, None)
    model_activate.change(lambda x: params.update({'model_output_activate': x}), model_activate, None)

    show_model_original_output.change(lambda x: params.update({'show_model_original_output': x}), show_model_original_output, None).then(
        toggle_text_in_history, gradio('history'), gradio('history')).then(
        chat.save_history, gradio('history', 'unique_id', 'character_menu', 'mode'), None).then(
        chat.redraw_html, gradio(ui_chat.reload_arr), gradio('display'))

    user_language.change(update_user, user_language, None)
    model_language.change(update_model, model_language, None)

def update_user(x):
    global user_to_model, model_to_user
    params.update({"user_language": language_codes[x]})
    user_to_model = GoogleTranslator(source=params['user_language'], target=params['model_language'])
    model_to_user = GoogleTranslator(source=params['model_language'], target=params['user_language'])

def update_model(x):
    global model_to_user, user_to_model
    params.update({"model_language": language_codes[x]})
    model_to_user = GoogleTranslator(source=params['model_language'], target=params['user_language'])
    user_to_model = GoogleTranslator(source=params['user_language'], target=params['model_language'])