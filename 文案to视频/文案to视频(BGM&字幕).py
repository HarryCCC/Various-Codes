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
我想自己是盖茨比。
我重新从解构里看盖茨比的故事，看中有时也会碰到想要泪下的机遇。我是说，我想自己也能追求着去做盖茨比那样的，最起码在为人与功利上做如此的展望。
他是黄土地的乡野里来的，就像我一样。不不，我是说，我像他，也想做到他那样的。只不过，他被赋予的过去，相比我的，还更难以要自己做到些什么。
泥腿子出身，严于律己，远赴重洋，然后回到总自以为的故乡，回到说同样的口音、吃同样的餐饭的地方，能实现自己曾经想要在这里实现什么梦的地方。他，我们，都似乎想证明什么。也许他是为了一个人，也许只是自驱的，而我不是，我想做这些，总是携着要反馈那些曾经给予过我什么的人的心中的远光。
我说即使是在小说里，他做到了，挟裹着比我更艰难的过去，却能成就我仍不敢于急忙确定的将来。但作品是艺术的，也许曾有过那么一个光亮的盖茨比，就在作者曾知晓的人际里，但也许这也只是一个心中的想，一次塑造。

我不想说也无法说我自己在以后的某一天就会能到达那么样的地方。但我所想的是，至少我想成为。
可我却自愧于没有故事里他的才华横溢与坚毅。我和他有哪些像，但我又无法像他那样为了心里的一束光而目标坚定，也自认做不到对一个人，乃至于为了那个人的一种向往所产生的如此尔尔的死心塌地。
我如今年少，自觉不如他。他年风正盛时住在五光十色的城堡里，双手把住舵轮陪聊得来的朋友兜风。但我理解他，理解他从荒芜中走出来的开拓性，想要改变自己与家人的境况的心意，心中为了一个人而要做什么的志向。所以我就像他一般的，等人走近了来，也许会被迫祛了魅，也会被人说着: 『原来这鲜衣怒马的小子，与我本没什么两样』。

人终究是要有一两个榜样的。我把直到遇到旧人之前的他，成就还未因不理性而散落前的他，在朝着心海中想象的灯塔模样地方进发的他，都当作我如今能参考的榜样。尽管心里的灯塔也许只是一束光的光彩，实际上没什么灯塔可以依仗。
他的死是冤屈的，但我们不知道在他忘记所有之前的最后几秒里是否也曾后悔。
我如今知道了盖茨比一直是在做些什么。
他从来划行在夜色永不退散的海洋上，那里是苍茫无垠的，自从心中想要追求的那束光出现，他就一直以为灯塔就在那边，永远等着自己去发现，去停泊。他很努力，比我所能做到与想象的还要再多一点，但直到自己尽心到筋疲力竭而后瘫倒在船面上之前，他都以为灯光就在那里。也许最后残喘的他终于躺在了狭隘的只能容下孤身的木舟中央，抬头望到上头，不知道是日光还是月色的一束，透过云层的边缘，绵绵地洒在他眼前。或许他也曾质疑过自己，尤其是在最劳顿的瞬间，『从前到现在走了好远，可那个方向真的是我一直想要到达的地方吗？』我想他一定对自己这么说过，但，『即便不继续行驶，除此之外，我还能做些什么呢？』无论他曾经付出得更多或更少，最终仍然只睡在了漆黑的海上的长夜里。

我想，盖茨比是我最极远最纯粹的尽头。
当我放眼头顶，那里没有分辨不出的云朵里透出的耀眼的光。我举眉望去，满目星河。我的前路不是一缕光所照明的。我比他前行得更慢一些，没有很累，也不觉得何时随时就要为行进而倾倒。所以我划得还要远些，最后也没有看到人言里的灯塔，却也觅得一处与自己足以堪伴后生的岛屿。
亲爱的，要说的话，夜色的确温柔，因为白昼太过热情。
又或许，夜色温柔，因为我们珍惜在夜色中所做的那些。
"""

video_folder = "Videos"
audio_folder = "Musics"

final_video_clip, similarity_info = process_video_and_similarity(text, video_folder)
with open("similarity_info.txt", "w", encoding="utf-8") as file:
    file.writelines(similarity_info)
final_video_with_subtitles = add_subtitles(final_video_clip, text)
final_video_with_subtitles.write_videofile("final_video_with_subtitles.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

