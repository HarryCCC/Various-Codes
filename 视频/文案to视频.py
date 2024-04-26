# -*- coding: utf-8 -*-
import os
import spacy
from transformers import BertTokenizer, BertModel
from moviepy.editor import concatenate_videoclips, VideoFileClip, vfx
import torch

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

def create_video_from_text(text, video_folder):
    video_embeddings = cache_video_embeddings(video_folder)
    used_videos = set()  # 用来存储已经使用过的视频

    punctuation_marks = {'.', ',', ';', ':', '。', '，', '；', '：'}
    count = 0
    start = 0
    segments = []

    for i, char in enumerate(text):
        if char in punctuation_marks:
            count += 1
            if count % 5 == 0:
                segments.append(text[start:i+1])
                start = i + 1

    if start < len(text):
        segments.append(text[start:])

    video_clips = []
    similarity_info = []

    for segment in segments:
        text_tags = extract_keywords(segment)
        text_length = len(segment.replace(" ", ""))
        expected_duration = text_length * 0.21554  # 每个字符N秒
        # text_length * 0.21554  # 柔美女友
        segment_embedding = get_embedding(segment)
        
        best_video = None
        highest_similarity = -1
        
        for video, (tags, video_embedding) in video_embeddings.items():
            if video not in used_videos:
                video_path = os.path.join(video_folder, video)
                clip = VideoFileClip(video_path)
                video_duration = clip.duration
                similarity = calculate_similarity(segment_embedding, video_embedding)

                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_video = video
                    best_tags = tags  # 保存最佳匹配视频的标签
                    best_clip = clip
                    best_video_duration = video_duration

        if not best_video:
            raise Exception("视频片段不足，请添加更多视频文件。")
        
        used_videos.add(best_video)  # 标记为已使用

        # Adjust video duration
        if best_video_duration > expected_duration:
            best_clip = best_clip.subclip(0, expected_duration)  # 截断视频
        else:
            playback_speed = best_video_duration / expected_duration
            best_clip = best_clip.fx(vfx.speedx, playback_speed)  # 调整播放速度

        # 确保在信息输出时使用标签列表
        similarity_info.append(f"Segment: {segment}\n \nTags: {text_tags}\nBest Video: {best_video}\nVideo Tags: {best_tags}\nSimilarity Score: {highest_similarity}\n\n\n")
        video_clips.append(best_clip)
        last_video = best_video

    with open("similarity_info.txt", "w", encoding="utf-8") as file:
        file.writelines(similarity_info)

    final_clip = concatenate_videoclips(video_clips)
    final_clip.write_videofile("final_video.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

text = """
 
举例，通过观察一个人对于多个事项的看法，我们为他贴上了“悲观主义者”的标签，而这样的标签在通常意义上看来，不被认为是一个能创造净潜在价值的，所以对于悲观主义，讨厌者可能多于倾好者。
 
再举例，通过与一个人的交流，了解到他和自己同来自于一个故乡城市，或者两人未来打算奔向的地方同处于一个接近的位置。此时的两人的关系会迅速升温的原因就是：他们都认为对方对于自己有相当概率是存在创造净潜在价值的机会的，且这种推断纳入了更多的主观成分，包括高估概率，忽略对方与自己在其他特点上的差异性（也许有些人不与自己有类似的来头或去处，却相比而言更有交际价值）。
 
讲来讲去倒成了理论阐述。此刻当我们再回到问题：“我爱你，是在爱你这个人吗？”
 
我想这句话在问的，大概更多是：“我爱你是因为爱你的脑袋吗？”或者“爱一个人的灵魂对于我判断自己爱不爱这个人来说有多重要？”
 
我想答案是简单的，“这很主观”。
 
这样的问题的答案会根据你处于任何不同的情境下而改变，比如情感状态（刚分手，已婚，恋情中，母胎单身），经济状况（穷困潦倒所以很看重货币，富裕所以不太在乎对方的经济能力），乃至于不同的人本身对于精神契合的需求度就不同（有人可以接受为漂亮媳妇端茶送饭，有人觉得话聊不上来再怎样也都是作罢）。
 
至于我，以前也许无所谓，而如今关于与人的爱，最狭义的灵魂与脑袋我看重四成，次狭义的人给外界的感知我看重四成，而至于其他标签我只看它是两成。

"""
video_folder = "Videos"
# 使用示例
create_video_from_text(text, video_folder)
