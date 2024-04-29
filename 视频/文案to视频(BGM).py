# -*- coding: utf-8 -*-
import os
import spacy
from transformers import BertTokenizer, BertModel
from moviepy.editor import concatenate_videoclips, VideoFileClip, vfx, concatenate_audioclips, AudioFileClip
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

def create_video_from_text(text, video_folder, audio_folder):
    video_embeddings = cache_video_embeddings(video_folder)
    text_keywords = extract_keywords(text)
    audio_details = load_mp3_files(audio_folder)
    audio_rankings = calculate_audio_relevance(audio_details, text_keywords)
    total_text_length = len(text.replace(" ", ""))
    expected_video_duration = total_text_length * 0.22
    selected_audios = select_audio_files(audio_rankings, expected_video_duration)
    
    used_videos = set()
    punctuation_marks = {'.', ',', ';', ':','!','?', '。', '，', '；', '：','！','？'}
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
    similarity_info = ["Selected Background Music:\n"]
    for filepath, duration in selected_audios:
        similarity_info.append(f"{os.path.basename(filepath)} - Duration: {duration}\n")

    similarity_info.append("\nVideo Segments and Similarities:\n")
    for segment in segments:
        text_tags = extract_keywords(segment)
        text_length = len(segment.replace(" ", ""))
        segment_embedding = get_embedding(segment)
        highest_similarity = -1
        best_video = None
        best_tags = []
        best_clip = None
        
        for video, (tags, video_embedding) in video_embeddings.items():
            if video not in used_videos:
                video_path = os.path.join(video_folder, video)
                clip = VideoFileClip(video_path)
                similarity = calculate_similarity(segment_embedding, video_embedding)
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    best_video = video
                    best_tags = tags
                    best_clip = clip

        if best_clip:
            expected_duration = text_length * 0.22
            best_video_duration = best_clip.duration
            if best_video_duration > expected_duration:
                best_clip = best_clip.subclip(0, expected_duration)  # Truncate the video
            else:
                playback_speed = best_video_duration / expected_duration
                best_clip = best_clip.fx(vfx.speedx, playback_speed)  # Adjust the playback speed

        used_videos.add(best_video)
        best_clip = best_clip.set_duration(text_length * 0.22)
        video_clips.append(best_clip)
        similarity_info.append(f"Segment: {segment}\nTags: {text_tags}\nBest Video: {best_video}\nVideo Tags: {best_tags}\nSimilarity Score: {highest_similarity}\n\n")

    final_video_clip = concatenate_videoclips(video_clips)
    background_audio = combine_audio_clips(selected_audios, final_video_clip.duration)
    final_video_clip = final_video_clip.set_audio(background_audio)
    
    with open("similarity_info.txt", "w", encoding="utf-8") as file:
        file.writelines(similarity_info)

    final_video_clip.write_videofile("final_video.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

text = """
『我才是自己嘲讽所的最大的怀疑论者。
我始终怀疑自己有哪些好处，
坚信自己才是最卑鄙的那个。』
前些日子里我对自己“害怕反馈，回避结果”有过反思，我说，“我怕自己会是那个没做到做好的人”。事实里，我对美好反馈实际是却之不恭的傲慢家伙。
"""
video_folder = "Videos"
audio_folder = "Musics"
create_video_from_text(text, video_folder, audio_folder)
