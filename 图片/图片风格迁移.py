import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models
from PIL import Image
import os
from torchvision.models import vgg19
from torchvision.models.vgg import VGG19_Weights
from tqdm import tqdm


# 定义设备：如果CUDA可用，则使用GPU，否则使用CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def gram_matrix(tensor):
    """计算给定特征图的Gram矩阵"""
    _, d, h, w = tensor.size()
    tensor = tensor.view(d, h * w)
    gram = torch.mm(tensor, tensor.t())
    return gram


def get_features(image, model, layers=None):
    """获取VGG19模型的中间层输出，作为内容和风格的特征"""
    if layers is None:
        layers = {'0': 'conv1_1', '5': 'conv2_1', '10': 'conv3_1', '19': 'conv4_1', '21': 'conv4_2', '28': 'conv5_1'}
    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x
    return features

def style_transfer(content_path, style_path, output_path, num_steps=100, style_weight=1e6, content_weight=1):
    # 加载预训练的VGG19模型
    vgg = vgg19(weights=VGG19_Weights.IMAGENET1K_V1).features.to(device).eval()


    # 图像预处理
    transform = transforms.Compose([
        transforms.Resize(400),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 加载内容和风格图像
    # 加载内容和风格图像，并确保它们只有RGB三个通道
    content_image = Image.open(content_path).convert("RGB")
    content = transform(content_image).unsqueeze(0).to(device)

    style_image = Image.open(style_path).convert("RGB")
    style = transform(style_image).unsqueeze(0).to(device)

    
    # 初始化目标图像为内容图像与随机噪声的混合
    target = content.clone().detach() * 0.6 + torch.randn_like(content).detach() * 0.4
    target.requires_grad_(True).to(device)

    # ... 这里是风格迁移的核心代码，包括特征提取、风格和内容损失的计算等 ...

    # 提取内容和风格图像的特征
    content_features = get_features(content, vgg)
    style_features = get_features(style, vgg)
    target_features = get_features(target, vgg)

    # 计算风格图像的Gram矩阵
    style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

    # 设置内容和风格的权重
    style_weights = {'conv1_1': 1., 'conv2_1': 0.8, 'conv3_1': 0.5, 'conv4_1': 0.3, 'conv5_1': 0.1}

    # 初始化内容和风格的损失
    content_loss = 0
    style_loss = 0

    # 对于每个目标特征层，计算内容和风格的损失
    for layer in target_features:
        # Content loss
        if layer == 'conv4_2':
            content_loss += torch.mean((target_features[layer] - content_features[layer]) ** 2)

        # Style loss
        if layer in style_weights:
            target_feature = target_features[layer]
            target_gram = gram_matrix(target_feature)
            style_gram = style_grams[layer]
            layer_style_loss = style_weights[layer] * torch.mean((target_gram - style_gram) ** 2)
            _, d, h, w = target_feature.shape
            style_loss += layer_style_loss / (d * h * w)

    # 计算总损失并优化
    total_loss = content_weight * content_loss + style_weight * style_loss

    # 使用优化器更新生成的图像
    optimizer = optim.LBFGS([target])
    
    def closure(retain_graph=False):
        optimizer.zero_grad()
        target_features = get_features(target, vgg)
        content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2']) ** 2)
        style_loss = 0
        for layer in style_weights:
            target_feature = target_features[layer]
            target_gram = gram_matrix(target_feature)
            style_gram = style_grams[layer]
            layer_style_loss = style_weights[layer] * torch.mean((target_gram - style_gram) ** 2)
            _, d, h, w = target_feature.shape
            style_loss += layer_style_loss / (d * h * w)
        total_loss = content_weight * content_loss + style_weight * style_loss
        total_loss.backward(retain_graph=retain_graph)

        return total_loss


    for step in tqdm(range(num_steps), desc="Optimizing Image"):
        optimizer.step(lambda: closure(retain_graph=True))



    # 在优化结束后clamp目标图像的值
    target.data.clamp_(0, 1)

    # 保存生成的图像
    final_transform = transforms.Compose([
        transforms.Normalize(mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225], std=[1/0.229, 1/0.224, 1/0.225]),
        transforms.ToPILImage()
    ])
    final_transform(target[0].cpu().clamp_(0, 1)).save(output_path)





# 使用示例
style_transfer('content.png', 'style.png', 'output.png')
