# -*- coding: utf-8 -*-
import os
import spacy
from transformers import BertTokenizer, BertModel
from moviepy.editor import concatenate_videoclips, VideoFileClip, vfx, concatenate_audioclips, AudioFileClip, TextClip, CompositeVideoClip
import torch
import librosa  # For audio file handling

# GPU设置
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 加载模型
nlp = spacy.load("zh_core_web_sm")
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese').to(device)

def extract_keywords(text):
    doc = nlp(text)
    return [token.text for token in doc if not token.is_stop and token.pos_ in {'NOUN', 'PROPN', 'ADJ', 'VERB'}]

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True, padding='max_length')
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze()

def calculate_similarity(embedding1, embedding2):
    cos = torch.nn.CosineSimilarity(dim=0)
    return cos(embedding1, embedding2).item()

def cache_video_embeddings(video_folder):
    video_embeddings = {}
    video_files = os.listdir(video_folder)
    for video in video_files:
        if video.endswith(".mp4"):
            # 确保标签被正确地以逗号分割
            tags = video.replace('.mp4', '').split(',')
            video_embedding = get_embedding(' '.join(tags))
            video_embeddings[video] = (tags, video_embedding)  # 保存标签列表和嵌入
    return video_embeddings

def load_mp3_files(audio_folder):
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
    audio_details = {}
    for audio in audio_files:
        filepath = os.path.join(audio_folder, audio)
        duration = librosa.get_duration(filename=filepath)
        audio_details[audio] = {
            'duration': duration,
            'filepath': filepath
        }
    return audio_details

def calculate_audio_relevance(audio_details, text_keywords):
    audio_rankings = []
    for audio, details in audio_details.items():
        # Extract keywords from the filename
        audio_tags = audio.replace('.mp3', '').split('-')
        # Calculate relevance (simple overlap of keywords)
        relevance = len(set(audio_tags) & set(text_keywords))
        audio_rankings.append((audio, relevance, details['duration'], details['filepath']))
    # Sort by relevance
    audio_rankings.sort(key=lambda x: -x[1])
    return audio_rankings

def select_audio_files(audio_rankings, expected_duration):
    total_duration = 0
    selected_audios = []
    for audio, relevance, duration, filepath in audio_rankings:
        if total_duration + duration <= expected_duration:
            selected_audios.append((filepath, duration))  # 修改这里，确保一致性
            total_duration += duration
        else:
            remaining_duration = expected_duration - total_duration
            if remaining_duration > 0:
                selected_audios.append((filepath, remaining_duration))
                total_duration += remaining_duration
            break
    return selected_audios

def combine_audio_clips(audio_paths, total_video_duration):
    clips = []
    current_duration = 0.0
    for audio_path, clip_duration in audio_paths:
        clip = AudioFileClip(audio_path)
        if clip.duration > clip_duration:
            clip = clip.subclip(0, clip_duration)
        clips.append(clip)
        current_duration += clip.duration
        if current_duration >= total_video_duration:
            break
    combined_clip = concatenate_audioclips(clips)
    return combined_clip

# 视频处理
def process_video_and_similarity(text, video_folder):
    video_embeddings = cache_video_embeddings(video_folder)
    text_keywords = extract_keywords(text)
    audio_details = load_mp3_files('Musics')
    audio_rankings = calculate_audio_relevance(audio_details, text_keywords)
    total_text_length = len(text.replace(" ", ""))
    expected_video_duration = total_text_length * 0.22
    selected_audios = select_audio_files(audio_rankings, expected_video_duration)

    similarity_info = ["Selected Background Music:\n"]
    for filepath, duration in selected_audios:
        similarity_info.append(f"{os.path.basename(filepath)} - Duration: {duration} seconds\n")

    punctuation_marks = {'.', ',', ';', ':', '!', '?', '。', '，', '；', '：', '！', '？'}
    count = 0
    start = 0
    segments = []
    video_clips = []
    used_videos = set()
    similarity_info.append("\nVideo Segments and Similarities:\n")

    for i, char in enumerate(text):
        if char in punctuation_marks:
            count += 1
            if count % 5 == 0:
                segment = text[start:i + 1]
                segments.append(segment)
                start = i + 1

    if start < len(text):
        segments.append(text[start:])

    for segment in segments:
        text_length = len(segment.replace(" ", ""))
        text_tags = extract_keywords(segment)
        segment_embedding = get_embedding(segment)
        expected_duration = text_length * 0.22
        highest_similarity = -1
        best_video = None
        best_clip = None
        best_tags = []

        for video, (tags, video_embedding) in video_embeddings.items():
            if video not in used_videos:
                similarity = calculate_similarity(segment_embedding, video_embedding)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_video = video
                    best_tags = tags
                    video_path = os.path.join(video_folder, video)
                    best_clip = VideoFileClip(video_path)

        if best_clip:
            best_video_duration = best_clip.duration
            if best_video_duration > expected_duration:
                best_clip = best_clip.subclip(0, expected_duration)
            else:
                playback_speed = best_video_duration / expected_duration
                best_clip = best_clip.fx(vfx.speedx, playback_speed)

            best_clip = best_clip.set_duration(expected_duration)
            video_clips.append(best_clip)
            used_videos.add(best_video)
            similarity_info.append(f"Segment: {segment}\nTags: {text_tags}\nBest Video: {best_video}\nVideo Tags: {best_tags}\nSimilarity Score: {highest_similarity}\n\n")

    final_video_clip = concatenate_videoclips(video_clips)
    background_audio = combine_audio_clips(selected_audios, final_video_clip.duration)
    final_video_clip = final_video_clip.set_audio(background_audio)
    return final_video_clip, similarity_info

def add_subtitles(video_clip, text, font_path='c:\WINDOWS\Fonts\MSYH.TTC'):
    subs = []
    punctuation_marks = {'.', ',', ';', ':', '!', '?', '。', '，', '；', '：', '！', '？'}
    count = 0
    start = 0
    subtitle_segments = []

    # 处理字幕分段，确保包括文本的最后一部分
    for i, char in enumerate(text):
        if char in punctuation_marks:
            count += 1
            if count % 3 == 0:
                subtitle_segments.append((start, i + 1))
                start = i + 1

    if start < len(text):  # 确保包括最后一个片段
        subtitle_segments.append((start, len(text)))

    # 计算并添加每个字幕
    total_duration = 0.0  # Track the total duration used by subtitles
    for index, (start, end) in enumerate(subtitle_segments):
        segment = text[start:end]
        text_length = len(segment.replace(" ", ""))
        segment_duration = text_length * 0.22
        # 修正字幕开始时间，避免重史
        start_time = total_duration
        total_duration += segment_duration
        if total_duration > video_clip.duration:
            segment_duration = video_clip.duration - start_time  # Adjust the last subtitle duration

        txt_clip = TextClip(segment, fontsize=48, color='white', font=font_path,
                            size=(video_clip.w, None), method='caption', align='center')
        txt_clip = txt_clip.set_position(('center', 0.75), relative=True).set_duration(segment_duration).set_start(start_time)
        subs.append(txt_clip)

    # 确保总的字幕时间不超过视频时长
    if total_duration > video_clip.duration:
        for sub in subs:
            sub.duration *= (video_clip.duration / total_duration)
            sub.end = sub.start + sub.duration

    final_clip = CompositeVideoClip([video_clip] + subs, size=video_clip.size)
    return final_clip

text = """
『我一直觉得，爱情最残忍的地方在于，从它发生的最初就已经到达巅峰。那种怦然心动，那种想要收割对方的强烈欲望，那种迫不及待想要到达未来的期许，都在恋爱的开始就已经被预支。从此往后，再怎么走都是下坡路。』
这是姐姐发来问我要观点的社会论题，我想，她是无法反驳这其中的道理的，否则也不至于就要轮到向我请教了。
我想，也只有如今的我才真正拥抱了一些些，一些回答这样问题的容量。以往我恐怕不会惦念太多关于情情爱爱，我甚至可能是要略有些把自己从感性里抽出来为她解读的，她也丝毫不会想到向着一个清脆的娃娃讨论情感，就像我们不会教育孩子关于抽烟酗酒。
但要如今的我于理性框架中解读感情，就如同要一个精通的魔术师在把玩卡牌的时候能循规蹈矩，也就像要求美丽的舞蹈家褪去她精心设计的服饰而穿上与舞台并不搭调的装扮。『当我身陷囹圄时，我唯一能想到的，也只有了逃脱。』

真的如此吗？我在想的是，当我入了被人囚禁的天日不寻的境界，我还是只会像每个囚犯的翻版一般吗？『我也只会一心求解吗？』
我固然不是的。我会想办法要自己做些什么，那可以是踩缝纫机，干劳务，做任何我会觉得会对我重获自由有益的事。我还会竭尽全力搞到更多我能寻到的读书学习的机会，尽力保持在一个才学的优势地位上。
所以，若如今我们就要强硬地把情感比作困人的囹圄之地，我们是否就要承纳往往常见的感情连接的模式？是否就要漠然地接受美好的畅想与爱，就那样地一去不复返呢？
我无法接受这样的状况，就像我无法接受她明天不再爱我那样。所以，我们应该做些什么，当是该做些什么才对？

我想，我今日可以偷个懒，用对于其他问题的我当下的答案，作为我们可以为了维护感情的美妙而付与的什么行动。
1.『爱，就是克制。那宽容是什么？宽容在爱里是什么？』
爱不是克制，但若你真的爱他，可以让自己试试学着克制，克制是一种爱的方式，并且绝对不是多数派的选择。
克制的反面不是宽容，而是放纵。克制是勒住自己的心，要我们的感情容器不会总想要向外溢出。情感是可以积累的，但若你总想着要它流出去得再快些快些，那就再积蓄不住了。而若真成了没有了爱的储蓄的情感关系，无非就是会要你觉得这事情变得平淡无味，变得我爱也好，不爱也罢。
我如此地解读关于爱与爱的积攒，也正能解释大姐对于爱的现象: “若是我能回去总看见他的本人，我想我会更有热情激情一些”，她如此描绘自己的病症。“因为你的每次见面都能为这段关系带来一些积累的『情』，所以你才如此。”可就像这样的，若是没了更多积累『情』的场景，是否就要接受情感储蓄的消磨殆尽？我想如今这在不同人心中也当有个答案。
至于『宽容』，如同我前文里提及的，宽容不是克制的反面，放纵才是。而宽容，就是克制本身。如此狭义的宽容的定义是: 『当我明白地克制自己的感情时，我也理应尊重你保持克制的合理性。』在宽容时，我们正是在克制自己对于『情』的合理不收受。

2.『想说时克制自己不说，这是延迟满足吗？延时满足的意义是？克制有意义吗？至少克制带来的“新鲜感”我认为被预期中地达到了。』
除了『情感积蓄』理论，还有广泛适用的『延迟满足』理论用于辩护情感中克制的优势。
我们为什么支持多数人学会延迟满足？有人或许要说: “我们学会延迟满足，就是为了要自己更像个人，而不是被需求驱动的动物。”这听起来有劝服性，但我想这在理性上经不起推敲。人本就是动物，也不认为自己最根本的欲望有任何的无道理，为何就应该要避免被认为是个被需求所驱动的动物呢？
『延迟满足』最大的意义是，它教人能『从最小的理性成本中，获取最大的感情效益』。这句道理是如此的具有美学特征，乃至于我不再愿意用阐述式的语言来表达它。就要我来举个最纯粹的例子吧: 一个孩子，给她在某个未来一场美食的机会，但目标是达成某个好成绩，那她也许能做到为了这样的目标而真正坚持每日的努力。这样的热情投入，这样最终的成就感萌发，到头看，只是一顿美餐的支出。这在纯粹理性的分析框架下是一场收益成本不对等的投入产出，但却能因为延迟满足的存在与执行，而使之真实成立。

3.『无法得到或还不曾得到的永远更好？是因为我们在想象中的拟造？』
于我而言，是的。所以，尽全力享受你仍能活在预期中的时候吧。

4.『冷静的爱，务必走得比轰烈的更远吗？』
最终到底是要看两人在主观与客观上的双重对接的。但，同样的两个人，采取更冷静的交往模式，至少应当可以让整个陪伴的人生中可感知的情感路段稍稍再长一些。简单说起来就是，起码会让纯粹感情上的爱的直觉更绵久一些。

5.『爱里的克制，与禁欲同样吗？如果我可以做到这样克制，这对于此时此刻的我，是好事吗？』
禁欲是用理智抵抗做一件欲望驱动的事情，而克制是约束情感外溢的频次与速率。如果我们认为情感外溢是一种源于欲望且被欲望指使的现象，那禁欲就是一种克制。
克制不一定能为每时每刻的你都带来综合效益上的净优势，但，学会克制一定能为你带来好处。最起码的是，你现在还没有学会。

X.『我一直觉得，爱情最残忍的地方在于，从它发生的最初就已经到达巅峰。那种怦然心动，那种想要收割对方的强烈欲望，那种迫不及待想要到达未来的期许，都在恋爱的开始就已经被预支。从此往后，再怎么走都是下坡路。』
让我们回到这样长长的社会论点吧，并在我们今日讨论的框架下，尝试回答它。
答案: 是基于个人行为模式而可能发生的情况，不适用于任何情境。
利用好『克制』这枚工具，你令自己再难遇到所谓的残忍的情感巅峰，也不会有那么想要“收割”对方，也可以学会在期许未来的同时避免“迫不及待”，最终更不必“预支或透支”未来的感情。
当我们轻松地把『情感储蓄』比作『金钱储蓄』，一切都是如此容易理解: 
放纵是用将来支持现下，而克制则是用现今支持未来。
"""

video_folder = "Videos"
audio_folder = "Musics"

final_video_clip, similarity_info = process_video_and_similarity(text, video_folder)
with open("similarity_info.txt", "w", encoding="utf-8") as file:
    file.writelines(similarity_info)
final_video_with_subtitles = add_subtitles(final_video_clip, text)
final_video_with_subtitles.write_videofile("final_video_with_subtitles.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

