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
        txt_clip = txt_clip.set_position(('center', 0.80), relative=True).set_duration(segment_duration).set_start(start_time)
        subs.append(txt_clip)

    # 确保总的字幕时间不超过视频时长
    if total_duration > video_clip.duration:
        for sub in subs:
            sub.duration *= (video_clip.duration / total_duration)
            sub.end = sub.start + sub.duration

    final_clip = CompositeVideoClip([video_clip] + subs, size=video_clip.size)
    return final_clip

text = """
『我才是自己嘲讽所的最大的怀疑论者。
我始终怀疑自己有哪些好处，
坚信自己才是最卑鄙的那个。』
前些日子里我对自己“害怕反馈，回避结果”有过反思，我说，“我怕自己会是那个没做到做好的人”。事实里，我对美好反馈实际是却之不恭的傲慢家伙。
可收到好消息，听到好夸赞，我心中或许兴奋几下里，却又能做到快快消散。
也许我能做到对人的情意悠久绵长，可我的情绪就如同乡村山野里的某一条溪流，它从哪里来，到哪里去，我都不明白。但我从中取一瓢饮，喝下就继续上路。情绪来得不愠不火，做事起来也能做到忘记或深或浅的念想。
这就是我的情绪，那就是没什么情绪。
霉头的事情来了，我摆摆手这不重要，就忘掉。快乐时候喜上眉梢，回头想想自己所庆幸的，马上要觉得自己没追求。

我想，这是『理性的代价』。
我曾说，我如今开始觉得孤独了，无非是忘记了“取悦自己”的手段。我近来对自己说: 『不为自己，所以努力』，我还说: 『我愿作环嶂，你为山庄』。我的确不懂得如何做些只为了自己的事情了。

说来说去我倒是离了题。但也不全是。
我说自己总不为自己而活，若是碰上个钟意的人，与人家交往，天天里要不停问自己一遍又一遍: 『她真的喜欢我吗？』『人对我倾注的感情总归有限度的。』『她会一直喜欢我吗？』
我考虑这些，也烦躁考虑这些的自己。讨厌这样的问题，因为自己的事情我总能估摸出个答案，可对于别人家，我想破头顶也是没有知会的。
日常里我有事无事难免想起在乎的人与事，『看吧，我有多卑鄙。』不过，『也许人家也会惦念我吗？』我没有答案，我希望是的。
即使要来个回答，也只能充我今日的饥，我后日里还会想。即使我再让自己确信，用行为与言辞的证据为自己的被喜爱所辩护，我还是恨自己的恶劣，『我不相信人能那么爱我』，我总这么想。
也许到我许了人家，做了丈夫，才能让自己稍微放心:『她至少应是有我母亲与我的一半那样爱我吧。』

夜里浑浑浊浊的脑袋里装不下转的动的思维，我又在前面写了长长无用的说法。权且当那些是对心里的每个念头的记下吧。

『我不是个赌徒』，这是一条我想回来用给自我形容的句子。
『没人愿意做赌徒，大概。』
我记起上次被谩怨不该给些什么模棱两可的话，这么说，我倒成了逼人做赌徒的坏人。是吧，理性人的赌博，总归是被环境所迫。
理性决策里的不确定性，于我而言只是一种基于利益的选择题。可感情里的绝对不是: 人可能会因为喜欢这个而放弃另一个，喜欢现有的而放弃潜在的。这绝对不是『对理性的抛弃』，反而可堪称得上为『理性化的感性』，因为对于只应该拥有一个的事物却持有超过一个，最终只会换来一无所有。理性化感性的不确定性是跳跃和离散的: 选择了确定性，就意味着放弃其他所有的关于这样的确定性的不确定性。

而我是个总对于不确定性抱有怀疑态度的人，或许只是思想的辩证，但我不会轻易劝服自己一种事实: “大概率发生的不确定性就是确定性”。这样说着，倒把自己驳倒了: 对于那些无限接近百分百真实的道理的不确定性，我仍认为它们是难以揣摩值得怀疑的吗？
只是不同的人对于不确定性与确定性之间的状态转换点或突变点的定位不同。有人认为90%就是稳中稳，有人觉得99%才足以劝服自己，这无关预期收益。试着想想: 你会选择 a. 90%得到一百块，10%失去九百块; 还是 b. 99%得到一百块，1%失去九千九百块？
在确定性超越了这样的人性的转折点之后，才能说这样的一个人对于某件事的观点达到了确信。

在谈过『怀疑』后，我本想说说对自己以及对外人的『相信』。但有趣的是，当我预想到自己的发问: “所以，为什么我们会不相信自己与对方呢？”，我仍难免会引用我刚提及的『确定性转换点』理论: 怀疑在概率上就体现为，不确定性予人的相信程度尚未达到确信拐点。
当然，我们也无法推定所有的怀疑论者就都是那些『确信拐点』阈值很高的。到底里，怀疑还与另一种概念相关: 『事物观点』。
一个对某事物采取『积极观点』的人在同一事宜上，本就与其他悲观主义者的概率认知完全不同。譬如我说我相信印度会在2050年前超越美国成为届时的综合第二国度这样事件的发生概率也许在我眼中是50%，而在一些亲米派的眼中可能只有10%甚至更低。那么即使我们二者的确信拐点相同，对这样同一件事的怀疑程度也是相差甚远的。
"""

video_folder = "Videos"
audio_folder = "Musics"

final_video_clip, similarity_info = process_video_and_similarity(text, video_folder)
with open("similarity_info.txt", "w", encoding="utf-8") as file:
    file.writelines(similarity_info)
final_video_with_subtitles = add_subtitles(final_video_clip, text)
final_video_with_subtitles.write_videofile("final_video_with_subtitles.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

