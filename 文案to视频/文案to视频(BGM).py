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
    expected_video_duration = total_text_length * 0.21554
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
            expected_duration = text_length * 0.21554
            best_video_duration = best_clip.duration
            if best_video_duration > expected_duration:
                best_clip = best_clip.subclip(0, expected_duration)  # Truncate the video
            else:
                playback_speed = best_video_duration / expected_duration
                best_clip = best_clip.fx(vfx.speedx, playback_speed)  # Adjust the playback speed

        used_videos.add(best_video)
        best_clip = best_clip.set_duration(text_length * 0.21554)
        video_clips.append(best_clip)
        similarity_info.append(f"Segment: {segment}\nTags: {text_tags}\nBest Video: {best_video}\nVideo Tags: {best_tags}\nSimilarity Score: {highest_similarity}\n\n")

    final_video_clip = concatenate_videoclips(video_clips)
    background_audio = combine_audio_clips(selected_audios, final_video_clip.duration)
    final_video_clip = final_video_clip.set_audio(background_audio)
    
    with open("similarity_info.txt", "w", encoding="utf-8") as file:
        file.writelines(similarity_info)

    final_video_clip.write_videofile("final_video.mp4", codec="h264_nvenc", ffmpeg_params=['-c:v', 'h264_nvenc', '-preset', 'fast'])

text = """
 
“我爱你，是在爱你这个人吗？”
 
近来有事可做，没能做到闲得发慌，前两天白日里偶然记得起的议题，深夜里终于得空能评判两下。
 
当我在这样发问时，我在问些什么？
 
我想，我不断要求自己想要知道的是，爱一个人，是指深深地爱着她那颗圆滚滚的脑袋吗？
 
当我们假设可以认定对方对自己是基本诚实的时候，那么她嘴里所说的，就应该距离其中思想里的真实相差无几。
 
看吧，我就说诚实总是爱情里最重要的一件事之一。没了这东西，人便成了只要相信那嘴里吐露出来的说法的玩艺儿，正与听听便信了的 AI 无异。
 
可即使我们真正地喜欢上了一个人脑袋里所想的，甚至是他脑袋这个本身，也即：他的性格，他的思维方式，他的表现手法，我全都欢喜。即使我们喜欢到这样的地步，我们能说，我们就爱上了一个人吗？
 
人的脑袋，是其天赋的智商与情商，与这样的人在后天所经历的一切，进行时刻不停的互动所达成的混沌。爱一个人的大脑，称得上我爱上了他吗？或者说，我爱一个人，终究是在爱他的脑子吗？
 
无论浪漫主义者和自视清高的家伙们如何反驳，大多数人都难以脱离这样的事实：人喜欢一个人，终究不是只爱她的脑袋。
 
从最狭义上说，一个人就是他的脑袋在某个时间时储存的一切。因为当我们在假设上拥有一套躯体培养系统或者缸中脑的器械的境遇下，人可以幻化成各种形态，甚至是非人的状态。
 
可矛盾而伤感的是，人的大脑中的思维模式是强烈依赖于“当下状态”与“过往记忆”而形成的。假如我们任意改变其中一个，就能根本性地扭转一个人类的思维。
 
举例，一个曾经身材优良的帅哥，如今在土木工程的摧残下，外加染上烟酒肉食，让体重面容难堪。他对于“当下状态”的成因，就能根据“过往记忆”形成极其明确的认知：假如我辞去现在的工作，戒掉再不该接触的东西，就有很大概率回归我最想的状态。
 
可同样的眼前境遇，一个从未减去过体重的天生肥胖者或者知道自己即使身强体健时的外观确实只有几斤几两的人，就完全对现状有不同的思维方向，也就导致了不同的动机与后续行为。这也许是解释：越好越变好，愈劣愈劣化 的一种理论。
 
次一级的关于“人本身”的狭义定义是：一个人的脑子里的一切，以及你能触碰到的关于他的躯体，以及他在你的面前时所能让你看到的所有的行动所透露的信息。
 
事实上，有一种更为简洁的定义办法：通过视觉，听觉，味觉，触觉，嗅觉的五官，你所能感知到的她的整个存在。
 
这通常是大多数人在中长期的交往里对于一个人的全面认识，以及对于“人”的认知。其实这样的对于人的感知当然相比最狭义会更加全面些，却会导致一些额外的问题，比如对于人的思维本身也就是对于人的脑袋的关注度与感知会更低。
 
幸运的是，现代科技辅助下，实时通讯促进了更频繁的语言沟通，而语言就是思维交流的最绝对重要载体。可惜的是，语言永远是不完全的。从思维到语言，需要经历大脑的“理解来信→推理→组织语言”的简化流程，仅仅如此，就难以避免信息的损失。更何况，存在不完全诚实的信息主动保留，这无法避免，因为人的诚实程度是从 0-99 的过程，百分百的诚实意味着不顾虑任何的意见表达，这应当是糟糕的。
 
更广义的关于“一个人”的定义可以是这样三件事的总和：一个人的脑袋，一个人留给人的感知印象，一个人所背负的任何具有潜在价值属性的标签。
 
人们对于标签的认可度或喜好程度，大抵可以被认为是基于人对于这样的标签的主观加客观的净潜在价值的正负性以及绝对值大小的认定。
 
举例，通过观察一个人对于多个事项的看法，我们为他贴上了“悲观主义者”的标签，而这样的标签在通常意义上看来，不被认为是一个能创造净潜在价值的，所以对于悲观主义，讨厌者可能多于倾好者。
 
再举例，通过与一个人的交流，了解到他和自己同来自于一个故乡城市，或者两人未来打算奔向的地方同处于一个接近的位置。此时的两人的关系会迅速升温的原因就是：他们都认为对方对于自己有相当概率是存在创造净潜在价值的机会的，且这种推断纳入了更多的主观成分，包括高估概率，忽略对方与自己在其他特点上的差异性（也许有些人不与自己有类似的来头或去处，却相比而言更有交际价值）。
 
讲来讲去倒成了理论阐述。此刻当我们再回到问题：“我爱你，是在爱你这个人吗？”
 
我想这句话在问的，大概更多是：“我爱你是因为爱你的脑袋吗？”或者“爱一个人的灵魂对于我判断自己爱不爱这个人来说有多重要？”
 
我想答案是简单的，“这很主观”。
 
这样的问题的答案会根据你处于任何不同的情境下而改变，比如情感状态（刚分手，已婚，恋情中，母胎单身），经济状况（穷困潦倒所以很看重货币，富裕所以不太在乎对方的经济能力），乃至于不同的人本身对于精神契合的需求度就不同（有人可以接受为漂亮媳妇端茶送饭，有人觉得话聊不上来再怎样也都是作罢）。
 
至于我，以前也许无所谓，而如今关于与人的爱，最狭义的灵魂与脑袋我看重四成，次狭义的人给外界的感知我看重四成，而至于其他标签我只看它是两成。

"""
video_folder = "Videos"
audio_folder = "Musics"
create_video_from_text(text, video_folder, audio_folder)
