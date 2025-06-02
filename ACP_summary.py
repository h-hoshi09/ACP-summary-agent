#ライブラリのインストール
import streamlit as st
from openai import OpenAI
import os
import io
import soundfile as sf 
import subprocess

#APIキーを設定
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.title("仮想ACP要約エージェント")

# チャット履歴を保存
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "あなたは親切なアシスタントです。"}]

def summarize_with_example(transcript):
    prompt = f"""
以下は看護師と患者の会話を要約した見本です：

[要約①]
大切にしている事は「落ち着いた環境で過ごせること」「痛みや苦しみが少なくなること」「人の迷惑にならないこと」「身の回りのことが自分でできること」「望んだ場所で過ごせること」を選択した。
本人からは「元気な時は妻と一緒に庭いじり、読書をしていた。今は呼吸が辛くて、外に出る機会も少なくなった」「妻も膝が悪い。長男と長女は遠くにいるけど、次男は市内にいて来てくれている。一番頼りになる」と話されていた。
自分の健康状態は理解できている。希望する治療について「肺を悪くしてから歩くのも辛い。苦しい事はこれ以上長くなるのは辛い。」と答えた。将来脳の障害等で自分の事を判断出来なくなった時は「深くは考えていない。
自分の家で生活したいけど、これ以上負担が増えて、家族に迷惑がかかるなら自宅以外での生活を選択する。」と答えた。病状が悪化した時、もしもの時は「迷惑を掛けたくない事を第一に考えている。
その時の状況で考えたい。その時の延命治療は希望しない」と答えた。代わりに意思決定してくれる方は「今は妻。次男にも相談していきたい。今まで話しをした事がないから、私の気持ちを理解しているかわからない」と答えた。
本人からは「次男は気に掛けてくれて、何かと頼りにしている。自分の事を妻にも話す機会がなかったから、今後は話していく。訪問看護を受けているけど、自分の空間に人を入れる事は苦手なんだよね」と答えた。

[要約②]
大切にしている事は「落ち着いた環境で過ごせること」「人の迷惑にならないこと」「自然に近い形で過ごすこと」「身の回りの事が自分でできること」を選択した。本人からは「30年間登山をしていた。孫が人いて、成長が楽しみです。妻とは長く連れ添っています。妻の体調も心配です」と答えた。
自分の健康状態について「理解しています。」と答えた。受ける治療の希望は「大きい手術をした事がない。自分の事が自分で出来るなら治療をしたいけど、これ以上迷惑を掛けたくないから動けなくなるなら大変な治療は希望しない。」と言われた。
将来脳の障害で自分で判断出来なくなった時の療養場所について「なるべく迷惑をかけずに自宅で生活したい」と希望された。本人からは「糖尿病がある。手術に向けてコントロールを頑張ります。手術が終わってからは美味しい物を食べたい。身の回りの事は妻が手伝ってくれる。妻も腰が悪いので迷惑をかけたくない。
息子は2人いるけど、どちらも自分の生活があるから頼れない。病気のことは一応伝えています」と話された。

以下の会話も上の要約を見本にして同じ構成で要約した文章にしてください。：

[会話]
{transcript}

[要約]
""".strip()

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# メッセージ送信処理
user_input = st.text_input("テキストを入力してください：", "")
if st.button("送信") and user_input:
    # ユーザーの発言を履歴に追加
    st.session_state.messages.append({"role": "user", "content": user_input})

    # OpenAI API 呼び出し
    response = client.chat.completions.create(
        model="gpt-4.1",  # gpt-4 に変更も可
        messages=st.session_state.messages
    )

    # アシスタントの返答を取得
    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})


#音声ファイルのアップデートと書き起こし
st.subheader("音声ファイルをアップロードして書き起こし")

audio_file = st.file_uploader("音声ファイルを選択（mp3, wav, m4a）", type=["mp3", "wav", "m4a"], key="audio")

if audio_file is not None:
   
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.read())
    
    if st.button("書き起こし実行"):
        # 外部スクリプト（別環境）で書き起こし
        result = subprocess.run(["python", "transcribe.py", "temp_audio.wav"])
        
        if os.path.exists("transcript.txt"):
            with open("transcript.txt", "r", encoding="utf-8") as f:
                transcript_text = f.read()
                st.text_area("書き起こし結果", transcript_text, height=200)
        
            # チャット履歴に送信
                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "system", "content": "あなたは親切なアシスタントです。"}]

                st.session_state.messages.append({"role": "user", "content": transcript_text})
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(f"**アシスタント:** {reply}")
        
        else:
            st.error("書き起こしに失敗しました。")

#テキストファイルのアップデート
st.subheader("テキストファイルをアップロードして要約")
text_file = st.file_uploader("テキストファイルを選択（.txt）", type=["txt"], key="text")

if text_file is not None and st.button("テキストファイルを要約"):
    file_content = text_file.read().decode("utf-8")
    
    # 表示切り替えチェックボックス（デフォルト: False）
    show_text = st.checkbox("アップロードしたテキストの内容を表示する", value=False)
    
    if show_text:
        st.text_area("アップロード内容", file_content, height=150)

    summary = summarize_with_example(file_content)
    st.session_state.messages.append({"role": "user", "content": f"[テキスト内容に基づいた要約依頼]\n{file_content}"})
    st.session_state.messages.append({"role": "assistant", "content": summary})
    st.markdown(f"**要約:** {summary}")


# チャット履歴の表示
st.subheader("チャット履歴")
for msg in st.session_state.messages[1:]:  # systemメッセージは表示しない
    if msg["role"] == "user":
        st.markdown("**あなた:**")
        st.text_area(label="", value=msg["content"], height=100, key=f"user_{hash(msg['content'])}")
    else:
        st.markdown(f"**アシスタント:** {msg['content']}")