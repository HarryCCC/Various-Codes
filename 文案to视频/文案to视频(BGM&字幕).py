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
人言，人孤独地来，孤独地走了，本就是一生孤独，孤独一生。是吗？
人越交流，只会觉得愈加孤独，是吗？
有些人是感受不了孤独的，最外向的家伙会采用各种办法避免自己陷入独身孑然的境地，而最内向的人们也会有消解自己的时间与取悦心灵的渠道。
而能感受到孤独的人，就像我这样的，对抗孤独的最大办法，就是接纳孤独吗？

我坐在金融学院里面西侧的一处躺椅上，周围没什么人，偶尔从我的左边的石灰地经过，从我的右侧走廊上渐进渐远，从我的眼前眉目下踱步。
说是躺椅，但这长椅一定是躺不了人的。设计师将一条条近乎于正方的木条按照规矩的间隔铺设在金属的框架上，再用铆钉扎住。我想着，它一定比我的人生更牢靠一些，我见它的模样，墩在这里许是有二十年往前的日子了。反正，这长椅一定是躺不了人的，人是活的，它是死的，我坐上去多待会就要觉得屁股硬板板的不舒服。
但我又不是挑剔到不行的怪异人，有人叫我提议去哪里聚会待着，我说草地空气清闲，天地入怀，不错。人说草地有些许脏了屁股吧。人说外边要是冷些怎样？我说冷冷的要人精神些，暖和了反而懈怠。所以今夜傍晚里我吹着深秋里夺人的凉风也不想走，五六点钟便没了夕照了，今天只有四点的阳光，五点的乌云，和六点的夜与夜空。
一阵来后，过会儿才能等到下一阵，就是这样的冷风，一样能打出我身上的战惊。但我也不想着回去吹吹空调的热气，做一顿腾腾的晚饭。我是喜欢晚上，还是喜欢凉风，还是喜欢晚风？我知道，我全都喜欢。当我听到人在近处远处活动时，我至少比独处房间内的自己更不孤独，人假使只是能看着我就好，我也不在意他们是谁，是否愿意认识我。
说是躺椅，但这长椅一定是躺不了人的。可我感受着屁股上有些的硌得慌的知觉，却不愿意起身走开。

我想起前些天小和对我说，“你在那里，能看到星星吗？我在这望着窗外。”我起身向外看，我当时没看到。如今我待到夜里，白灰色的云彩铺遍我能看到的一片天，我看到两颗远远的星星，我想不出比喻，也不觉她们在张望我。中间有一颗若有若现的，我猜是架飞机，但说是星星也不一定。这么说起来，我倒觉得看星星的话浪漫了。可无论如何我们能看到的都不是同一片星星，不浪漫在此，浪漫也在此。我认定以为这样的说法算得上情话的自己便是个没脑袋的家伙，但假若我能这么想呢？起码这话叫今天的我想起来还是温柔的。

风忽的要吹得大起来，我身前的草垛随着晃悠悠，再上面有棵不高不矮不细不粗的树竿，我觉得我像她，但，我现在要回家了。微微的凉风吹得人心醉，但若是风气再冷些，就教人坐不住了。风善变，但有些东西是不变的，就像我屁股下面的木椅座，纹丝不动，脊背也要觉得硌得慌了。
所以这风要吹得稍微凉快些才让人欢喜，太热太冷都不行。我也算因此记起来些道理。所以我建议这木椅还能再软和些。
"""

video_folder = "Videos"
audio_folder = "Musics"

final_video_clip, similarity_info = process_video_and_similarity(text, video_folder)
with open("similarity_info.txt", "w", encoding="utf-8") as file:
    file.writelines(similarity_info)
final_video_with_subtitles = add_subtitles(final_video_clip, text)
final_video_with_subtitles.write_videofile("final_video_with_subtitles.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

