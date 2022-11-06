import argparse
import cv2
import numpy as np
import torch
import time

from pytorch_grad_cam import GradCAM, \
    ScoreCAM, \
    GradCAMPlusPlus, \
    AblationCAM, \
    XGradCAM, \
    EigenCAM, \
    EigenGradCAM, \
    LayerCAM, \
    FullGrad

import torchvision # You may need to install separately
from torchvision import models

from torch.profiler import profile, record_function, ProfilerActivity

def run_gradcam(model, number_of_inputs, use_cuda=False):
    min_time = 10000000000000
    max_time = 0
    sum_of_times = 0

    dev = torch.device('cpu')
    if use_cuda:
        dev = torch.device('cuda:0')

    # TODO: Use real data?
    # TODO: Configurable dimensions?

    # Some defaults I use in research code
    input_tensor = torch.rand((number_of_inputs, 3, 256, 60))
    batch_size = 8
    targets = None # [ClassifierOutputTarget(None)]

    model.to(dev)
    target_layers = [model.layer4] # Last CNN layer of ResNet50

    cam_function = GradCAM(model=model, target_layers=target_layers, use_cuda=use_cuda)
    cam_function.batch_size = batch_size

    for i in range(number_of_inputs):
        start_time = time.time()

        # Actual code to benchmark
        input_image = input_tensor[i].to(dev)
        heatmap = cam_function(input_tensor=input_image, targets=targets)

        end_time = time.time()
        time_difference = end_time - start_time

        sum_of_times += time_difference

        if time_difference > max_time:
            max_time = time_difference

        if time_difference < min_time:
            min_time = time_difference

    avg_time = sum_of_times / number_of_inputs
    return [min_time, max_time, avg_time]

number_of_inputs = 1000
model =  models.resnet50()

# TODOs:
# Test with numpy v1.4.6 (master)
# Test with torch v1.4.7 (wip)
# Test other CAMs besides GradCAM
# Nice output

# Run on CPU with profiler (save the profile to print later)
with profile(activities=[ProfilerActivity.CPU], profile_memory=True, record_shapes=True) as prof:
    cpu_profile_min_time, cpu_profile_max_time, cpu_profile_avg_time = run_gradcam(model, number_of_inputs, use_cuda=False)
cpu_profile = prof.key_averages().table(sort_by="self_cpu_memory_usage", row_limit=15)

# Run on CUDA with profiler (save the profile to print later)
with profile(activities=[ProfilerActivity.CPU], profile_memory=True, record_shapes=True) as prof:
    cuda_profile_min_time, cuda_profile_max_time, cuda_profile_avg_time = run_gradcam(model, number_of_inputs, use_cuda=True)
cuda_profile = prof.key_averages().table(sort_by="self_cpu_memory_usage", row_limit=15)

# Run on CPU x1000 (get min, max, and avg times)
cpu_min_time, cpu_max_time, cpu_avg_time = run_gradcam(model, number_of_inputs, use_cuda=False)

# Run on CUDA x1000
cuda_min_time, cuda_max_time, cuda_avg_time = run_gradcam(model, number_of_inputs, use_cuda=True)

breakpoint()
