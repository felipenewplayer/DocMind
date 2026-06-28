import markdown as md

def get_css() -> str:
    
    return """
<style>
 @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    * {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #212121;
        color: #ececec;
    }
    .chat-container {
        max-width: 750px;
        margin: 0 auto;
        padding-bottom: 120px;
    }

    .msg-user {
        background-color: #111;
        border-radius: 16px;
        padding: 12px 18px;
        margin: 8px 0 8px 80px;
        color: #ececec;
        font-size: 15px;
        line-height: 1.6;
    }

    .msg-bot {
        background-color: #212121;
        border-radius: 16px;
        padding: 12px 18px;
        margin: 8px 80px 8px 0;
        color: #ececec;
        font-size: 16px;
        line-height: 2.0;
    }

    .stChatInput textarea {
        background-color: #21f2f2f !important;
        color: #ececec !important;
        border: 2px solid #3f3f3f !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        padding-left: 10px
    }

    .chat-title {
        text-align: center;
        color: #1cbcac;
        font-size: 60px;
        font-weight: 550;
        padding: 0px 0 25px;
        
    }

    .chat-subtitle {
        text-align: center;
        color: #8e8ea0;
        font-size: 15px;
        margin-bottom: 30px
    }
</style>
"""


def render_user_message(content: str) -> str:
    content_html = md.markdown(content, extensions=["nl2br", "sane_lists"])    
    return (
        f'<div class="msg-label">Você :</div>'
        f'<div class="msg-user">{content_html}</div>'
    )


def render_bot_message(content: str) -> str:
    return (
        f'<div class="msg-label">Assistente :</div>'
        f'<div class="msg-bot">{content}</div>'
    )


def render_header():
    title = '<div class="chat-title">DocMind</div>'
    subtitle = f'''<div class="chat-subtitle">
         Adicione seus documentos e receba respostas precisas com base no conteúdo.
    </div>'''
    return title, subtitle